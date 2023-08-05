from ..qc.opcode import OPCODE
from .dispatch import dispatch_table


class VirtualMachine:

    def __init__(self, debug=False, dispatch=dispatch_table):
        self.mem = []
        self.stack = []
        #self.channels = defaultdict(Channel)
        self.sp = 0  # stack pointer
        self.bp = 0  # base pointer
        self.sl = 0  # static link
        self.pc = 0  # program counter
        self.clk = 0
        self.debug = debug
        self.dispatch = dispatch

        self._dispatch_register = {
            OPCODE._SP: 'sp',
            OPCODE._BP: 'bp',
            OPCODE._SL: 'sl',
            OPCODE._PC: 'pc',
            OPCODE._WRITE_SP: 'sp',
            OPCODE._WRITE_BP: 'bp',
            OPCODE._WRITE_SL: 'sl',
            OPCODE._WRITE_PC: 'pc',
        }

    def _next(self):
        self.pc += 1
        return self.mem[self.pc - 1]

    def _pop(self):
        self.sp -= 1
        return self.stack[self.sp]

    def _push(self, value):
        if len(self.stack) > self.sp:
            self.stack[self.sp] = value
        else:
            self.stack.append(value)
        self.sp += 1

    def _pick(self, n=0):
        return self.stack[self.sp - n - 1]

    def _play(self):
        frame = self._pop()
        pulse = self._pop()

    def _captrue(self):
        frame = self._pop()
        cbit = self._pop()

    def display(self):
        if not self.debug:
            return
        print(f'State[{self.clk}] ====================')
        print(f'      OP: ', self.mem[self.pc])
        print(f'   STACK: ', self.stack[:self.sp])
        print(f'      BP: ', self.bp)
        print(f'      SL: ', self.sl)
        print(f'      PC: ', self.pc)
        print('')

    def trace(self):
        if not self.debug:
            return
        self.display()

    def run(self, code, step_limit=-1):
        if len(code) > len(self.mem):
            self.mem.extend([0] * (len(code) - len(self.mem)))
        for i, c in enumerate(code):
            self.mem[i] = c
        self.sp = 0  # stack pointer
        self.bp = 0  # base pointer
        self.sl = 0  # static link
        self.pc = 0  # program counter
        self.clk = 0  # clock

        while True:
            self.trace()
            op = self._next()
            if self.clk == step_limit:
                break
            self.clk += 1
            if isinstance(op, OPCODE):
                if op in self.dispatch:
                    self.dispatch[op](self)
                elif op == OPCODE.NOP:
                    continue
                elif op == OPCODE.EXIT:
                    break
                elif op in [OPCODE._SP, OPCODE._BP, OPCODE._SL, OPCODE._PC]:
                    self._push(getattr(self, self._dispatch_register[op]))
                elif op in [
                        OPCODE._WRITE_SP, OPCODE._WRITE_BP, OPCODE._WRITE_SL,
                        OPCODE._WRITE_PC
                ]:
                    setattr(self, self._dispatch_register[op], self._pop())
                else:
                    raise RuntimeError(f"unknown command {op}")
            else:
                self._push(op)
