import dace
import json
import islpy as isl

from pathlib import Path

from scop2sdfg.sdfg_generator import SDFGGenerator, BuildFns
from scop2sdfg.llvm2sdfg import ctype2dtype

from daisy.passes import PipelineFactory


def scop2sdfg(
    source_path: str, scop: str, transfer_tune: bool = False, topK: int = 1
) -> str:
    source_path = Path(source_path)
    source_dir = source_path.parent
    filename = source_path.name

    scop = json.loads(scop)

    print(scop)

    # Create SDFG
    sdfg = dace.SDFG(
        ("sdfg_" + filename + "_" + scop["name"])
        .replace(".", "")
        .replace("%", "")
        .replace("-", "_")
    )
    sdfg.build_folder = str(source_dir / sdfg.name / "dacecache")

    # Adding arrays and symbols
    symbols = set()
    for array in scop["arrays"]:
        name = array["name"]
        sizes = array["sizes"]
        ctype = array["type"]
        dtype = ctype2dtype(ctype)

        shape = []
        for val in sizes:
            if val == "*":
                new_symbol = "_N" + str(len(symbols))
                sdfg.add_symbol(new_symbol, stype=dace.int64)
                symbols.add(new_symbol)

                shape.append(new_symbol)
            elif val.startswith("%"):
                new_symbol = "_S" + str(len(symbols))
                sdfg.add_symbol(new_symbol, stype=dace.int64)
                symbols.add(new_symbol)

                shape.append(new_symbol)
            else:
                shape.append(int(val))

        sdfg.add_array(name, shape=shape, dtype=dtype, transient=False)

    # Define dependencies
    ctx = isl.DEFAULT_CONTEXT
    raw = isl.UnionMap.read_from_str(ctx, scop["dependencies"]["RAW"])
    war = isl.UnionMap.read_from_str(ctx, scop["dependencies"]["WAR"])
    waw = isl.UnionMap.read_from_str(ctx, scop["dependencies"]["WAW"])
    dependencies = raw.union(war).union(waw)

    # Union of statement domains
    domains = None
    for statement in scop["statements"]:
        if domains is None:
            domains = isl.UnionSet.read_from_str(ctx, statement["domain"])
        else:
            domains = domains.union(
                isl.UnionSet.read_from_str(ctx, statement["domain"])
            )

    # Scop Schedule
    schedule = isl.UnionMap.read_from_str(ctx, scop["schedule"])
    schedule = schedule.intersect_domain(domains)

    context = isl.Set.read_from_str(isl.DEFAULT_CONTEXT, scop["context"])
    ast = BuildFns.get_ast_from_schedule_map(dependencies, schedule, context)

    init_state = sdfg.add_state(is_start_state=True)
    SDFGGenerator.parse(sdfg, ast, scop, init_state)

    # Canonicalize SDFG
    sdfg.openmp_sections = False
    sdfg.simplify()

    # Prune unprofitable
    if len(sdfg.states()) == 1 and not sdfg.start_state.nodes():
        return ""

    # Compile SDFG
    sdfg.specialize({sym: 1024 for sym in sdfg.symbols if str(sym).startswith("_N")})

    if transfer_tune:
        pipeline = PipelineFactory.static(topK=topK)
        try:
            pipeline.apply_pass(sdfg, {})
        except:
            return ""

    sdfg.compile()
    sdfg.save(source_dir / sdfg.name / f"{sdfg.name}.sdfg")

    return sdfg.name
