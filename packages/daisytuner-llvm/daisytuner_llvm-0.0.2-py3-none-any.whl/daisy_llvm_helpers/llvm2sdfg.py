import dace
import struct

from typing import Union, List

_DTYPES = {
    "double": dace.float64,
    "float": dace.float32,
    "i64": dace.int64,
    "i32": dace.int32,
    "i16": dace.int16,
    "i8": dace.int8,
    "ptr": dace.int32,
}


def _convert_condition(condition: str):
    if condition == "olt":
        return "<"
    elif condition == "oeq":
        return "=="
    elif condition == "ole":
        return "<="
    elif condition == "eq":
        return "=="
    elif condition == "ne":
        return "!="
    elif condition == "slt":
        return "<"
    elif condition == "ult":
        return "<"
    else:
        raise ValueError("Unsupported condition: ", condition)


def is_var(expr: str):
    return expr.startswith("%")


def variable_renaming(var: Union[str, List]):
    if isinstance(var, str):
        return var.strip().replace("%", "_").replace(".", "")
    elif isinstance(var, list):
        return [variable_renaming(k) for k in var]


def ctype2dtype(ctype: str):
    return _DTYPES[ctype]


def inst2tasklet(inst: str):
    output, inst = inst.split("=")
    output = output.strip()
    inst = inst.strip()

    output = variable_renaming(output)
    tokens = inst.split()

    if inst.startswith("load"):
        return None
    elif inst.startswith("store"):
        input = tokens[2].replace(",", "")
        if is_var(input):
            input = variable_renaming(input)
            inputs = [input]
        else:
            inputs = None
        return "store", f"{output} = {input}", inputs, output
    elif inst.startswith("fneg"):
        argument = tokens[-1]
        if is_var(argument):
            argument = variable_renaming(argument)
            inputs = [argument]
        else:
            inputs = []

        return "neg", f"{output} = -1 * {argument}", inputs, output
    # Binary
    elif inst.startswith("add") or inst.startswith("fadd"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        return "add", f"{output} = {arguments[0]} + {arguments[1]}", inputs, output
    elif inst.startswith("sub") or inst.startswith("fsub"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        return "sub", f"{output} = {arguments[0]} - {arguments[1]}", inputs, output
    elif inst.startswith("mul") or inst.startswith("fmul"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        return "mul", f"{output} = {arguments[0]} * {arguments[1]}", inputs, output
    elif inst.startswith("udiv") or inst.startswith("sdiv") or inst.startswith("fdiv"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        return "div", f"{output} = {arguments[0]} / {arguments[1]}", inputs, output
    elif inst.startswith("urem") or inst.startswith("srem") or inst.startswith("frem"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        return "rem", f"{output} = {arguments[0]} % {arguments[1]}", inputs, output
    elif inst.startswith("shl"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        return "shl", f"{output} = {arguments[0]} << {arguments[1]}", inputs, output
    elif inst.startswith("and"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        return "and", f"{output} = {arguments[0]} & {arguments[1]}", inputs, output
    elif inst.startswith("or"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        return "or", f"{output} = {arguments[0]} | {arguments[1]}", inputs, output
    elif inst.startswith("xor"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        return "xor", f"{output} = {arguments[0]} ^ {arguments[1]}", inputs, output
    # Conversion
    elif inst.startswith("sitofp"):
        inputs = variable_renaming([tokens[-3]])
        return "sitofp", f"{output} = float({inputs[0]})", inputs, output
    elif inst.startswith("fptosi"):
        inputs = variable_renaming([tokens[-3]])
        return "fptosi", f"{output} = int({inputs[0]})", inputs, output
    elif inst.startswith("sext"):
        inputs = variable_renaming([tokens[-3]])
        return "sext", f"{output} = {inputs[0]}", inputs, output
    elif inst.startswith("zext"):
        inputs = variable_renaming([tokens[-3]])
        return "zext", f"{output} = {inputs[0]}", inputs, output
    elif inst.startswith("trunc"):
        inputs = variable_renaming([tokens[-3]])
        return "trunc", f"{output} = {inputs[0]}", inputs, output
    elif inst.startswith("fpext"):
        inputs = variable_renaming([tokens[-3]])
        return "fpext", f"{output} = {inputs[0]}", inputs, output
    elif inst.startswith("fptrunc"):
        inputs = variable_renaming([tokens[-3]])
        return "fptrunc", f"{output} = {inputs[0]}", inputs, output
    # Conditional
    elif inst.startswith("select"):
        inputs = variable_renaming(
            [
                tokens[-5].replace(",", ""),
                tokens[-3].replace(",", ""),
                tokens[-1].replace(",", ""),
            ]
        )
        return (
            "select",
            f"{output} = {inputs[1]} if {inputs[0]} else {inputs[2]}",
            inputs,
            output,
        )
    elif inst.startswith("icmp"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        condition = tokens[1]
        condition = _convert_condition(condition)
        return (
            "icmp",
            f"{output} = {arguments[0]} {condition} {arguments[1]}",
            inputs,
            output,
        )
    elif inst.startswith("fcmp"):
        arguments = []
        inputs = []
        for arg in tokens[-2:][::1]:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        condition = tokens[1]
        condition = _convert_condition(condition)
        return (
            "fcmp",
            f"{output} = {arguments[0]} {condition} {arguments[1]}",
            inputs,
            output,
        )
    # Calls
    elif (
        inst.startswith("call")
        or inst.startswith("tail")
        or inst.startswith("musttail")
        or inst.startswith("notail")
    ):
        function_pos = None
        for i, token in enumerate(tokens):
            if token.startswith("@"):
                function_pos = i
                break

        function = " ".join(tokens[function_pos:])
        arguments_ = function[function.find("(") + 1 : function.find(")")].split(",")
        arguments_ = [arg[-arg[::-1].find(" ") :] for arg in arguments_]

        arguments = []
        inputs = []
        for arg in arguments_:
            arg = arg.replace(",", "")
            if is_var(arg):
                arg = variable_renaming(arg)
                inputs.append(arg)
            elif arg.startswith("0x"):
                arg = struct.unpack("!d", bytes.fromhex(arg[2:]))[0]

            arguments.append(arg)

        if function.startswith("@llvm.fmuladd"):
            return (
                "fmuladd",
                f"{output} = {arguments[0]} * {arguments[1]} + {arguments[2]}",
                inputs,
                output,
            )
        elif function.startswith("@llvm.floor"):
            return (
                "floor",
                f"{output} = floor({arguments[0]})",
                inputs,
                output,
            )
        elif function.startswith("@llvm.smax"):
            return (
                "smax",
                f"{output} = max({arguments[0]}, {arguments[1]})",
                inputs,
                output,
            )
        elif function.startswith("@llvm.smin"):
            return (
                "smin",
                f"{output} = min({arguments[0]}, {arguments[1]})",
                inputs,
                output,
            )
        elif function.startswith("@llvm.fabs"):
            return (
                "fabs",
                f"{output} = abs({arguments[0]})",
                inputs,
                output,
            )
        else:
            raise ValueError("Unknown function", inst)
    else:
        raise ValueError("Unknown instruction: ", inst, output)


def wcr_conversion(op: str, code: str, inputs: List[str], output: str):
    inputs = sorted(inputs, key=lambda item: code.find(item))
    if op == "fmuladd":
        code = f"{output} = {inputs[0]} * {inputs[1]}"
        return "mul", code, inputs, output, "lambda x,y: x + y"
    if op == "fcmp_fused_select":
        code = f"{output} = {inputs[0]}"
        return "mul", code, inputs, output, "lambda x,y: min(x, y)"
    else:
        raise ValueError("Unsupported WCR conversion: ", code)
