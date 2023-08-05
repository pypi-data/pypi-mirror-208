class Memory():
    def __init__(self, size):
        self._size = size
        self._mem = bytearray(size)

    def read(self, addr, size=1):
        return self._mem[addr:addr + size]

    def write(self, addr, data):
        self._mem[addr:addr + len(data)] = data

    def __getitem__(self, addr):
        return self._mem[addr]

    def __setitem__(self, addr, value):
        self._mem[addr] = value

