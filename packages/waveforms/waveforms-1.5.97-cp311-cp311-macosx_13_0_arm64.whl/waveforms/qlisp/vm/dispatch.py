from ..qc.opcode import OPCODE


def vm_pop(vm):
    vm._pop()


def vm_dup(vm):
    x = vm._pop()
    vm._push(x)
    vm._push(x)


def vm_swap(vm):
    v2 = vm._pop()
    v1 = vm._pop()
    vm._push(v2)
    vm._push(v1)


def vm_over(vm):
    x = vm._pop()
    y = vm._pop()
    vm._push(y)
    vm._push(x)
    vm._push(y)


def vm_sload(vm):
    level = vm._pop()
    n = vm._pop()
    addr = vm.bp
    for _ in range(level):
        addr = vm.stack[addr - 3]
    vm._push(vm.stack[addr + n])


def vm_sstore(vm):
    level = vm._pop()
    n = vm._pop()
    value = vm._pop()

    addr = vm.bp
    for _ in range(level):
        addr = vm.stack[addr - 3]
    vm.stack[addr + n] = value


def vm_load(vm):
    addr = vm._pop()
    vm._push(vm.mem[addr])


def vm_store(vm):
    addr = vm._pop()
    value = vm._pop()
    vm.mem[addr] = value


def vm_call(vm):
    func = vm._pop()
    argc = vm._pop()
    args = [vm._pop() for _ in range(argc)]

    if callable(func):
        vm._push(func(*args))
    elif isinstance(func, int):
        vm._push(vm.bp)
        vm._push(vm.sl)
        vm._push(vm.pc)
        vm.bp = vm.sp
        for arg in reversed(args):
            vm._push(arg)
        vm.sl = func
        vm.pc = func
    else:
        raise RuntimeError(f"not callable {func}")


def vm_ret(vm):
    result = vm._pop()
    vm.sp = vm.bp - 3
    vm.bp, vm.sl, vm.pc = vm.stack[vm.bp - 3:vm.bp]
    vm._push(result)


def vm_call_ret(vm):
    func = vm._pop()
    argc = vm._pop()

    if callable(func):
        args = reversed(vm.stack[vm.sp - argc:vm.sp])
        vm.sp = vm.bp - 3
        vm.bp, vm.sl, vm.pc = vm.stack[vm.bp - 3:vm.bp]
        vm._push(func(*args))
    elif isinstance(func, int):
        if vm.sp != vm.bp + argc:
            vm.stack[vm.bp:vm.bp + argc] = vm.stack[vm.sp - argc:vm.sp]
            vm.sp = vm.bp + argc
        vm.sl = func
        vm.pc = func
    else:
        raise RuntimeError(f"not callable {func}")


def vm_jmp(vm):
    vm.pc = vm._pop() + vm.sl


def vm_jne(vm):
    addr = vm._pop()
    cond = vm._pop()
    if cond:
        vm.pc = addr + vm.sl


def vm_je(vm):
    addr = vm._pop()
    cond = vm._pop()
    if cond == 0:
        vm.pc = addr + vm.sl


dispatch_table = {
    OPCODE.DUP: vm_dup,
    OPCODE.DROP: vm_pop,
    OPCODE.SWAP: vm_swap,
    OPCODE.OVER: vm_over,
    OPCODE.SLOAD: vm_sload,
    OPCODE.SSTORE: vm_sstore,
    OPCODE.LOAD: vm_load,
    OPCODE.STORE: vm_store,
    OPCODE.CALL: vm_call,
    OPCODE.RET: vm_ret,
    OPCODE.CALL_RET: vm_call_ret,
    OPCODE.JMP: vm_jmp,
    OPCODE.JNE: vm_jne,
    OPCODE.JE: vm_je,
}

