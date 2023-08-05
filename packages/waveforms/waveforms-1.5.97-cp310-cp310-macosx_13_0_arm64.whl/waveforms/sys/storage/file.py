import io

from .chunk import (CHUNKSIZE, load_chunk, load_pack_chunk, pack_chunk,
                    pack_reader, pack_writer, save_chunk)


class File(io.RawIOBase):
    def __init__(self, file: str, mode: str = 'r', compressed: bool = False):
        super().__init__()
        self.file = file
        self.mode = mode
        self.compressed = compressed
        self.pos = 0
        self.closed = False
        self.pack = None
        self.pack_reader = None
        if self.mode == 'r':
            if self.file.endswith('.pack'):
                self.pack = self.file
                self.pack_reader = pack_reader(self.pack)
            else:
                self.file = load_chunk(self.file, self.compressed)
        elif self.mode == 'w':
            self.file = io.BytesIO()
        elif self.mode == 'a':
            self.file = load_chunk(self.file, self.compressed)
            self.file = io.BytesIO(self.file)

    def read(self, size: int = -1) -> bytes:
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if self.mode != 'r':
            raise ValueError('File not open for reading')
        if self.pack is None:
            if size == -1:
                data = self.file[self.pos:]
                self.pos = len(self.file)
                return data
            else:
                data = self.file[self.pos:self.pos + size]
                self.pos += size
                return data
        else:
            if size == -1:
                size = CHUNKSIZE
            data = load_pack_chunk(self.pack_reader, self.pos, size)
            self.pos += size
            return data

    def write(self, data: bytes) -> int:
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if self.mode not in ['w', 'a']:
            raise ValueError('File not open for writing')
        self.file.write(data)
        return len(data)

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if whence == io.SEEK_SET:
            self.pos = offset
        elif whence == io.SEEK_CUR:
            self.pos += offset
        elif whence == io.SEEK_END:
            self.pos = len(self.file) + offset
        return self.pos

    def close(self) -> None:
        if self.mode == 'w':
            self.file.seek(0)
            