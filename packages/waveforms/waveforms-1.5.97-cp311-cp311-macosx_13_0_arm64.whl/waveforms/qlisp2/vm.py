class VirtualMachine():
    def __init__(self, code, stack, env):
        self.code = code
        self.stack = stack
        self.env = env
        self.pc = 0
        self.running = True

    def run(self):
        while self.running:
            self.step()

    def step(self):
        if self.pc >= len(self.code):
            self.running = False
            return
        instr = self.code[self.pc]
        self.pc += 1
        instr(self)

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def lookup(self, name):
        return self.env[name]

    def define(self, name, value):
        self.env[name] = value

    def call(self, func, args):
        return func(*args)

    def ret(self, value):
        self.stack.append(value)
        self.running = False

    def halt(self):
        self.running = False