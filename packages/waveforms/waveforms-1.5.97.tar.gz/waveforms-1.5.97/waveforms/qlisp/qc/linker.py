from .opcode import OPCODE


def _link(code, functions, constants):

    def process(code):
        count = 0
        tmp = []
        labels = {}
        pointers = {}
        functions = {}
        for c in code:
            if isinstance(c, str) and c.startswith('label:'):
                labels[c[6:]] = count
            else:
                count += 1
                tmp.append(c)
                if isinstance(c, str) and c.startswith(':'):
                    pointers[count] = c[1:]
        for i, label in pointers.items():
            if label in labels:
                tmp[i - 1] = labels[label]
            else:
                functions[i - 1] = label
        return tmp, functions

    for name in list(functions.keys()):
        if isinstance(functions[name], tuple):
            continue
        functions[name] = process(functions[name])

    fun_ptrs = {}
    const_ptrs = {}
    code, fun_refs = process(code)

    for name, value in constants.items():
        const_ptrs[name] = len(code)
        code.append(value)

    for name, (c, f_refs) in functions.items():
        fun_ptrs[name] = len(code)
        code.extend(c)
        for i, n in f_refs.items():
            fun_refs[i + fun_ptrs[name]] = n
    external_refs = {}
    for addr, label in fun_refs.items():
        if label in fun_ptrs:
            code[addr] = fun_ptrs[label]
        elif label in const_ptrs:
            code[addr] = const_ptrs[label]
        else:
            external_refs[addr] = label
    return code, external_refs


def link(functions=None, constants=None, dynamic=False):
    if functions is None:
        functions = {}
    if constants is None:
        constants = {}
    if "main" not in functions and not dynamic:
        raise RuntimeError("main function not defined")

    enter_code = [0, ":main", OPCODE.CALL, OPCODE.EXIT]
    code, external_refs = _link(enter_code, functions, constants)
    if external_refs and not dynamic:
        raise RuntimeError(
            f"external references: {set(external_refs.values())}")
    return code
