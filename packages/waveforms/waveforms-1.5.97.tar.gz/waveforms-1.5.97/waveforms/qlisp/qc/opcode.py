from enum import Enum, auto

cmp_op = ('<', '<=', '==', '!=', '>', '>=')

hasconst = []
hasname = []
hasjrel = []
hasjabs = []
haslocal = []
hascompare = []
hasfree = []
hasnargs = [] # unused

opmap = {}
opname = ['<%r>' % (op,) for op in range(256)]

def def_op(name, op):
    opname[op] = name
    opmap[name] = op

def name_op(name, op):
    def_op(name, op)
    hasname.append(op)

def jrel_op(name, op):
    def_op(name, op)
    hasjrel.append(op)

def jabs_op(name, op):
    def_op(name, op)
    hasjabs.append(op)

def_op('POP', 1)
def_op('DUP', 2)
def_op('SWAP', 3)
def_op('ROT', 4)
def_op('ROT2', 5)
def_op('ROT3', 6)
def_op('CALL', 7)
def_op('CALL_RET', 8)
def_op('RET', 9)
def_op('JMP', 10)
def_op('JE', 11)
def_op('JNE', 12)


del def_op, name_op, jrel_op, jabs_op


class OPCODE(Enum):
    NOP = auto()
    DUP = auto()
    DROP = auto()
    SWAP = auto()
    OVER = auto()
    SLOAD = auto()
    SSTORE = auto()
    LOAD = auto()
    STORE = auto()
    CALL = auto()
    RET = auto()
    CALL_RET = auto()
    JMP = auto()
    JNE = auto()
    JE = auto()
    EXIT = auto()

    # Waveform operators
    PLAY = auto()
    CAPTURE = auto()
    DELAY = auto()
    SET_PHASE = auto()
    ADD_PHASE = auto()
    SET_TIME = auto()
    BARRIER = auto()
    PLAY_ARRAY = auto()

    # Register commands
    _SP = auto()
    _BP = auto()
    _SL = auto()
    _PC = auto()
    _WRITE_SP = auto()
    _WRITE_BP = auto()
    _WRITE_SL = auto()
    _WRITE_PC = auto()

    def __repr__(self):
        return self.name

