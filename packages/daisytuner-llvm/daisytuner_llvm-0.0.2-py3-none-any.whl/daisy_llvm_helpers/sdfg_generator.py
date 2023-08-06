import copy
import dace
import sympy
import islpy as isl

from typing import Set, Dict

from dace.frontend.python.astutils import negate_expr
from dace.transformation.interstate import (
    InlineSDFG,
    LoopToMap,
    MoveLoopIntoMap,
    StateFusion,
)
from dace.transformation.optimizer import Optimizer
from dace.transformation.dataflow import (
    AugAssignToWCR,
    TaskletFusion,
    MapCollapse,
    TrivialTaskletElimination,
)

from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
)

from scop2sdfg.sympy_utils import to_sympy, sympy_to_pystr, extract_end_cond
from scop2sdfg.llvm2sdfg import inst2tasklet, variable_renaming, is_var


class SDFGGenerator:
    def __init__(self, sdfg: dace.SDFG, scop: Dict):
        self.sdfg = sdfg
        self.scop = scop
        self.inputs = set()
        self.outputs = set()
        self.loops = []

    def _visit(self, ast_node: isl.AstNode, loop_ranges, constraints):
        if ast_node.get_type() == isl.ast_node_type.block:
            first, last = self._visit_block(ast_node, loop_ranges, constraints)
        elif ast_node.get_type() == isl.ast_node_type.for_:
            first, last = self._visit_for(ast_node, loop_ranges, constraints)
        elif ast_node.get_type() == isl.ast_node_type.if_:
            first, last = self._visit_if(ast_node, loop_ranges, constraints)
        elif ast_node.get_type() == isl.ast_node_type.user:
            first, last = self._visit_user(ast_node, loop_ranges, constraints)
        else:
            raise NotImplementedError
        return first, last

    def _visit_block(self, ast_node: isl.AstNode, loop_ranges, constraints):
        node_list = ast_node.block_get_children()
        n_children = node_list.n_ast_node()

        states = []
        for child_node in [node_list.get_at(i) for i in range(n_children)]:
            ret_val = self._visit(child_node, loop_ranges.copy(), constraints)
            s1, s2 = ret_val
            states.append((s1, s2))

        if states:
            for (_, s1), (s2, _) in zip(states[:-1], states[1:]):
                self.sdfg.add_edge(s1, s2, dace.sdfg.InterstateEdge())
            return states[0][0], states[-1][1]
        else:
            empty_state = self.sdfg.add_state(f"block_{len(self.sdfg.nodes())}")
            return empty_state, empty_state

    def _visit_for(self, ast_node: isl.AstNode, loop_ranges, constraints):
        iter_sympy = to_sympy(ast_node.for_get_iterator())
        iterator_var = sympy_to_pystr(iter_sympy)
        self.loops.append(iterator_var)

        init_sympy = to_sympy(ast_node.for_get_init())
        init_str = sympy_to_pystr(init_sympy)

        cond_sympy = to_sympy(ast_node.for_get_cond())
        end_sympy = extract_end_cond(cond_sympy, iter_sympy)
        condition_str = sympy_to_pystr(cond_sympy)

        step_sym = to_sympy(ast_node.for_get_inc())
        incr_str = sympy_to_pystr(sympy.Add(iter_sympy, step_sym))

        loop_rng = dace.subsets.Range([(init_sympy, end_sympy, step_sym)])
        loop_ranges.append((iterator_var, loop_rng))

        is_parallel = ast_node.get_annotation().user.is_parallel
        if is_parallel:
            state = self.sdfg.add_state(f"MapState_{len(self.sdfg.nodes())}")
            subset = loop_rng

            map_nodes = dace.nodes.Map(
                label="map", params=[iterator_var], ndrange=subset
            )

            entry = dace.nodes.MapEntry(map_nodes)
            exit = dace.nodes.MapExit(map_nodes)
            state.add_nodes_from([entry, exit])

            # create a new SDFG for the map body
            body_sdfg = dace.SDFG("{}_body".format(entry.label))

            # add all arrays of SDFG to the body-SDFG
            for arr_label, arr in self.sdfg.arrays.items():
                arr_copy = copy.deepcopy(arr)
                arr_copy.transient = False

                body_sdfg.add_datadesc(arr_label, arr_copy)

            body_sdfg.symbols.update(self.sdfg.symbols)

            # walk and add the states to the body_sdfg
            pv = SDFGGenerator(sdfg=body_sdfg, scop=self.scop)
            pv.loops = self.loops
            (
                _,
                _,
            ) = pv._visit(ast_node.for_get_body(), loop_ranges.copy(), constraints)
            body = state.add_nested_sdfg(body_sdfg, self.sdfg, pv.inputs, pv.outputs)

            for arr_name in pv.inputs:
                if arr_name not in body.in_connectors:
                    continue
                read_node = state.add_read(arr_name)
                arr = body_sdfg.arrays[arr_name]
                subset = dace.subsets.Range.from_array(arr)
                memlet = dace.Memlet(data=arr_name, subset=subset)

                state.add_memlet_path(
                    read_node,
                    entry,
                    body,
                    memlet=memlet,
                    dst_conn=arr_name,
                    propagate=False,
                )
            if len(body.in_connectors) == 0:
                state.add_edge(entry, None, body, None, dace.Memlet())

            for arr_name in pv.outputs:
                if arr_name not in body.out_connectors:
                    continue
                write_node = state.add_write(arr_name)
                arr = body_sdfg.arrays[arr_name]
                subset = dace.subsets.Range.from_array(arr)
                memlet = dace.Memlet(data=arr_name, subset=subset)

                state.add_memlet_path(
                    body,
                    exit,
                    write_node,
                    memlet=memlet,
                    src_conn=arr_name,
                    dst_conn=None,
                    propagate=False,
                )
            if len(body.out_connectors) == 0:
                state.add_edge(body, None, exit, None, dace.Memlet())

            for arr in list(body_sdfg.arrays.keys()):
                if arr not in body.in_connectors and arr not in body.out_connectors:
                    body_sdfg.remove_data(arr, validate=False)

            self.inputs.update(pv.inputs)
            self.outputs.update(pv.outputs)

            self.loops.pop(-1)
            return state, state
        else:
            body_begin, body_end = self._visit(
                ast_node.for_get_body(), loop_ranges.copy(), constraints
            )

            if iterator_var not in self.sdfg.symbols:
                self.sdfg.add_symbol(iterator_var, dace.dtypes.int64)

            if body_begin == body_end:
                body_end = None

            loop_result = self.sdfg.add_loop(
                before_state=None,
                loop_state=body_begin,
                loop_end_state=body_end,
                after_state=None,
                loop_var=iterator_var,
                initialize_expr=init_str,
                condition_expr=condition_str,
                increment_expr=incr_str,
            )
            before_state, guard, after_state = loop_result

            self.loops.pop(-1)
            return before_state, after_state

    def _visit_if(self, ast_node: isl.AstNode, loop_ranges, constraints):
        # Add a guard state
        if_guard = self.sdfg.add_state("if_guard")
        end_if_state = self.sdfg.add_state("end_if")

        # Generate conditions
        if_cond_sym = to_sympy(ast_node.if_get_cond())
        if_cond_str = sympy_to_pystr(if_cond_sym)
        else_cond_sym = negate_expr(if_cond_sym)
        else_cond_str = sympy_to_pystr(else_cond_sym)

        then_node = ast_node.if_get_then_node()
        if_constraints = constraints.copy()
        if_constraints.append(if_cond_sym)
        first_if_state, last_if_state = self._visit(
            then_node, loop_ranges.copy(), if_constraints
        )

        # Connect the states
        self.sdfg.add_edge(
            if_guard, first_if_state, dace.sdfg.InterstateEdge(if_cond_str)
        )
        self.sdfg.add_edge(last_if_state, end_if_state, dace.sdfg.InterstateEdge())

        if ast_node.if_has_else_node():
            else_node = ast_node.if_get_else_node()
            else_constraints = constraints.copy()
            else_constraints.append(else_cond_sym)
            first_else_state, last_else_state = self._visit(
                else_node, loop_ranges.copy(), else_constraints
            )

            # Connect the states
            self.sdfg.add_edge(
                if_guard, first_else_state, dace.sdfg.InterstateEdge(else_cond_str)
            )
            self.sdfg.add_edge(
                last_else_state, end_if_state, dace.sdfg.InterstateEdge()
            )
        else:
            self.sdfg.add_edge(
                if_guard, end_if_state, dace.sdfg.InterstateEdge(else_cond_str)
            )
        return if_guard, end_if_state

    def _visit_user(self, ast_node: isl.AstNode, loop_ranges, constraints):
        ast_expr = ast_node.user_get_expr()
        if ast_expr.get_op_type() == isl.ast_expr_op_type.call:
            stmt_name = ast_expr.get_op_arg(0).to_C_str()
            stmt = None
            for s in self.scop["statements"]:
                if s["name"] == stmt_name:
                    stmt = s
                    break
            assert stmt is not None

            # Mapping domain dims to iter vars
            itervars = []
            repl_dict = {}
            domain = isl.Set.read_from_str(isl.DEFAULT_CONTEXT, stmt["domain"])
            dom_vars = list(domain.get_var_dict())

            for i in range(0, ast_expr.get_op_n_arg() - 1):
                new_var = ast_expr.get_op_arg(i + 1)
                if new_var.get_type() != isl.ast_expr_type.id:
                    continue

                var = dom_vars[len(repl_dict)]
                old_sym = dace.symbolic.pystr_to_symbolic(var)
                itervars.append(old_sym)

                repl_dict[old_sym] = dace.symbolic.pystr_to_symbolic(new_var.to_C_str())

            # Obtaining induction variables
            indvars = {}
            for i, loop_var in enumerate(self.loops):
                ind_var = stmt["loops"][i]["induction_variable"]
                ind_var = ind_var.strip().split("=")[0]
                ind_var = variable_renaming(ind_var)
                indvars[ind_var] = loop_var

            state = self.sdfg.add_state("state_" + stmt["name"])

            bb_inst = list(
                map(
                    lambda inst: inst.strip(),
                    stmt["basic_block"].splitlines(),
                )
            )
            stmt_inst = list(
                map(
                    lambda inst: inst.strip(),
                    stmt["stmt"].splitlines(),
                )
            )
            inst_map = {}
            for inst in stmt_inst:
                inst = inst.split("=")
                if len(inst) != 2:
                    continue

                inst_map[variable_renaming(inst[0])] = inst[1].strip()

            read_access_nodes = {}
            write_access_nodes = {}
            reads = {}
            writes = {}
            writes_inst = []
            for access in stmt["accesses"]:
                # { Stmt2[i0, i1, i2] -> MemRef2[512i0 + i2] }
                acc = access["relation"][1:-1].split("->")[-1].strip()
                # MemRef2
                array = acc[: acc.index("[")]
                # 512i0 + i2
                expr = acc[acc.index("[") : acc.index("]") + 1][1:-1]
                transformations = standard_transformations + (
                    implicit_multiplication_application,
                )
                if not expr:
                    if array not in self.sdfg.arrays:
                        dtype = dace.float64
                        for arr in self.sdfg.arrays:
                            if arr in array:
                                dtype = self.sdfg.arrays[arr].dtype
                                break

                        self.sdfg.add_scalar(name=array, dtype=dtype, transient=False)

                    expr = "0"

                sym_expr = parse_expr(
                    expr,
                    transformations=transformations,
                    local_dict={str(s): s for s in itervars},
                )
                # MemRef2[512 * i0 + i2]
                if not isinstance(sym_expr, (list, tuple)):
                    sym_expr = [sym_expr]

                sym_expr = list(map(lambda se: se.subs(repl_dict), sym_expr))
                memlet_expr = ",".join([str(dim) for dim in sym_expr])
                expr = array + f"[{memlet_expr}]"

                access_inst = access["access_instruction"].strip()
                if "load" in access_inst:
                    var, *_ = access_inst.split()
                    var = variable_renaming(var.replace(",", ""))

                    if array not in read_access_nodes:
                        read_access_nodes[array] = state.add_read(array)
                        self.inputs.add(array)

                    assert var not in reads
                    reads[var] = (array, expr)
                elif "store" in access_inst:
                    new_var = f"%out{len(writes)}"

                    if array not in write_access_nodes:
                        write_access_nodes[array] = state.add_write(array)
                        self.outputs.add(array)

                    access_inst = new_var + " = " + access_inst
                    writes_inst.append(access_inst)

                    writes[variable_renaming(new_var)] = (array, expr)
                elif "phi" in access_inst:
                    if access["kind"] == "read":
                        var, *_ = access_inst.split()
                        var = variable_renaming(var.replace(",", ""))

                        if array not in read_access_nodes:
                            read_access_nodes[array] = state.add_read(array)
                            self.inputs.add(array)

                        assert var not in reads
                        reads[var] = (array, expr)
                    else:
                        access_inst = access_inst[
                            access_inst.find("[") + 1 : -1
                        ].strip()
                        access_inst = (
                            access_inst.replace("[", "")
                            .replace("]", "")
                            .replace(" ", "")
                        )
                        vals = access_inst.split(",")

                        new_var = f"%out{len(writes)}"
                        if len(vals) == 2:
                            var, _ = vals
                            new_inst = new_var + " = " + f"store float {var}"
                        else:
                            var1, _, var2, _ = vals
                            if is_var(var2) and variable_renaming(var2) in inst_map:
                                new_inst = new_var + " = " + f"store float {var2}"
                            elif is_var(var1) and variable_renaming(var1) in inst_map:
                                new_inst = new_var + " = " + f"store float {var1}"
                            elif not is_var(var1):
                                new_inst = new_var + " = " + f"store float {var1}"
                            else:
                                continue

                        writes_inst.append(new_inst)

                        if array not in write_access_nodes:
                            write_access_nodes[array] = state.add_write(array)
                            self.outputs.add(array)

                        writes[variable_renaming(new_var)] = (array, expr)

            if not writes:
                # Cleanup
                for arr, node in read_access_nodes.items():
                    self.inputs.remove(arr)
                    state.remove_node(node)

                return state, state

            inst_map = {}
            for inst in bb_inst:
                inst = inst.split("=")
                if len(inst) != 2:
                    continue

                inst_map[variable_renaming(inst[0])] = inst[1].strip()

            tasklets = {}
            for inst in writes_inst:
                # LLVM IR -> python
                desc = inst2tasklet(inst)
                if desc is None:
                    continue

                op, code, inputs, output = desc

                # Define tasklet
                tasklet = state.add_tasklet(
                    op,
                    inputs=set(inputs) if inputs is not None else None,
                    outputs=set([output]),
                    code=code,
                )

                if inputs is not None:
                    for input in inputs:
                        self.find_input_and_connect(
                            state,
                            tasklet,
                            input,
                            tasklets,
                            reads,
                            read_access_nodes,
                            indvars,
                            inst_map,
                        )

                if output in writes:
                    array, expr = writes[output]
                    state.add_edge(
                        tasklet,
                        output,
                        write_access_nodes[array],
                        None,
                        dace.Memlet(data=array, expr=expr),
                    )
                else:
                    tasklets[output] = tasklet

            return state, state
        else:
            raise NotImplementedError

    @staticmethod
    def parse(
        sdfg: dace.SDFG,
        ast: isl.AstNode,
        scop: Dict,
        init_state: dace.SDFG,
    ):
        parser = SDFGGenerator(sdfg=sdfg, scop=scop)

        first, last = parser._visit(ast, [], [])
        sdfg.add_edge(init_state, first, dace.sdfg.InterstateEdge())

        dace.propagate_memlets_sdfg(sdfg)

        # Optimization
        # sdfg.apply_transformations_repeated(TrivialTaskletElimination, validate=False)
        while True:
            xforms = Optimizer(sdfg).get_pattern_matches(patterns=(TaskletFusion,))
            target = None
            for xform in xforms:
                state = xform._sdfg.node(xform.state_id)
                if state.out_degree(xform.t1) == 1:
                    target = xform
                    break

            if target is None:
                break

            target.apply(state, xform._sdfg)

        # sdfg.apply_transformations_repeated(
        #     (AugAssignToWCR, LoopToMap, InlineSDFG, StateFusion), validate=False
        # )
        sdfg.apply_transformations_repeated(
            (LoopToMap, InlineSDFG, StateFusion), validate=False
        )

        # Opt Pipeline
        sdfg.simplify()
        sdfg.apply_transformations_repeated(
            (MoveLoopIntoMap, LoopToMap, InlineSDFG), validate=False
        )
        # sdfg.apply_transformations_repeated(
        #     (AugAssignToWCR, LoopToMap, InlineSDFG, StateFusion), validate=False
        # )
        sdfg.simplify()
        sdfg.apply_transformations_repeated(MapCollapse)

        return last

    def find_input_and_connect(
        self,
        state: dace.SDFGState,
        tasklet: dace.nodes.Tasklet,
        input: str,
        tasklets: Dict[str, dace.nodes.Tasklet],
        reads: Dict[str, str],
        reads_access_nodes: Dict[str, dace.nodes.AccessNode],
        indvars: Dict[str, dace.nodes.MapEntry],
        bb: Dict[str, str],
    ):
        if input in reads:
            array, expr = reads[input]
            state.add_edge(
                reads_access_nodes[array],
                None,
                tasklet,
                input,
                dace.Memlet(data=array, expr=expr),
            )
        elif input in tasklets:
            tasklet_ = tasklets[input]
            if len(list(state.out_edges_by_connector(tasklet_, input))) == 0:
                state.add_edge(
                    tasklet_,
                    input,
                    tasklet,
                    input,
                    dace.Memlet(expr=None, data=None),
                )
            else:
                duplicated_tasklet = copy.deepcopy(tasklet_)
                state.add_edge(
                    duplicated_tasklet,
                    input,
                    tasklet,
                    input,
                    dace.Memlet(expr=None, data=None),
                )
                for inp in duplicated_tasklet.in_connectors:
                    self.find_input_and_connect(
                        state,
                        duplicated_tasklet,
                        inp,
                        tasklets,
                        reads,
                        reads_access_nodes,
                        indvars,
                        bb,
                    )

        elif input in indvars:
            indvar = indvars[input]

            ind_tasklet = state.add_tasklet(
                input, inputs=None, outputs=set([input]), code=f"{input} = {indvar}"
            )
            tasklets[input] = ind_tasklet

            state.add_edge(
                ind_tasklet,
                input,
                tasklet,
                input,
                dace.Memlet(expr=None, data=None),
            )
        elif input in bb:
            inst = f"{input} = {bb[input]}"
            op, code, inputs, output = inst2tasklet(inst)
            tasklet_ = state.add_tasklet(
                op,
                inputs=set(inputs) if inputs is not None else None,
                outputs=set([output]),
                code=code,
            )
            tasklets[input] = tasklet_
            del bb[input]

            state.add_edge(
                tasklet_,
                input,
                tasklet,
                input,
                dace.Memlet(expr=None, data=None),
            )
            for inp in inputs:
                self.find_input_and_connect(
                    state,
                    tasklet_,
                    inp,
                    tasklets,
                    reads,
                    reads_access_nodes,
                    indvars,
                    bb,
                )
        else:
            raise ValueError("Input not found: ", input)


class BuildFns:
    """
    Helper Class to generate a synthetic AST from the polyhedral representation.
    Functionality for tiling and detecting parallelism in synthetic AST.
    """

    deps = [None]

    class UserInfo:
        def __init__(self):
            # Loops is parallel
            self.is_parallel = False
            self.build = None
            self.schedule = None
            self.domain = None

    @staticmethod
    def at_each_domain(node: isl.AstNode, build: isl.AstBuild):
        """
        Annotated each node in the AST with the domain and partial schedule
        """
        info = BuildFns.UserInfo()
        id = isl.Id.alloc(ctx=isl.AstBuild.get_ctx(build), name="", user=info)
        info.build = isl.AstBuild.copy(build)
        info.schedule = build.get_schedule()
        info.domain = info.schedule.domain()
        node.set_annotation(id)
        return node

    @staticmethod
    def before_each_for(build: isl.AstBuild):
        """
        Detection of parallel loops.
        This function is called for each for in depth-first pre-order.
        """

        # A (partial) schedule for the domains elements for which part of
        # the AST still needs to be generated in the current build.
        # The domain elements are mapped to those iterations of the loops
        # enclosing the current point of the AST generation inside which
        # the domain elements are executed.
        part_sched = build.get_schedule()
        info = BuildFns.UserInfo()

        # Test for parallelism
        info.is_parallel = BuildFns.is_parallel(part_sched, BuildFns.deps[0])
        info.build = isl.AstBuild.copy(build)
        info.schedule = part_sched
        info.domain = part_sched.domain()

        return isl.Id.alloc(ctx=build.get_ctx(), name="", user=info)

    @staticmethod
    def is_parallel(part_sched: isl.UnionMap, stmt_deps: isl.UnionMap) -> bool:
        """
        Check if the current scheduling dimension is parallel by verifying that
        the loop does not carry any dependencies.
        :param part_sched: A partial schedule
        :param stmt_deps: The dependencies between the statements
        :return True if current the scheduling dimension is parallel, else False
        """

        # translate the dependencies into time-space, by applying part_sched
        time_deps = stmt_deps.apply_range(part_sched).apply_domain(part_sched)

        # the loop is parallel, if there are no dependencies in time-space
        if time_deps.is_empty():
            return True

        time_deps = isl.Map.from_union_map(time_deps)
        time_deps = time_deps.flatten_domain().flatten_range()

        curr_dim = time_deps.dim(isl.dim_type.set) - 1
        # set all dimension in the time-space equal, except the current one:
        # if the distance in all outer dimensions is zero, then it
        # has to be zero in the current dimension as well to be parallel
        for i in range(curr_dim):
            time_deps = time_deps.equate(isl.dim_type.in_, i, isl.dim_type.out, i)

        # computes a delta set containing the differences between image
        # elements and corresponding domain elements in the time_deps.
        time_deltas = time_deps.deltas()

        # the loop is parallel, if there are no deltas in the time-space
        if time_deltas.is_empty():
            return True

        # The loop is parallel, if the distance is zero in the current dimension
        delta = time_deltas.plain_get_val_if_fixed(isl.dim_type.set, curr_dim)
        return delta.is_zero()

    @staticmethod
    def get_annotation_build(ctx: isl.Set, deps: isl.UnionMap) -> isl.AstBuild:
        """
        helper function that return an isl.AstBuild
        """
        build = isl.AstBuild.from_context(ctx)
        # callback at_each_domain will be called for each domain AST node
        build, _ = build.set_at_each_domain(BuildFns.at_each_domain)
        BuildFns.deps = [deps]
        # callback before_each_for be called in depth-first pre-order
        build, _ = build.set_before_each_for(BuildFns.before_each_for)
        return build

    @staticmethod
    def get_ast_from_schedule_map(
        deps: isl.UnionMap, schedule_map: isl.UnionMap, context: isl.Set
    ):
        ctx = schedule_map.get_ctx()
        ctx.set_ast_build_atomic_upper_bound(True)
        ctx.set_ast_build_detect_min_max(True)

        build = BuildFns.get_annotation_build(context, deps)
        root = build.node_from_schedule_map(schedule_map)
        return root
