import hashlib
import lzma
import zlib
from io import BufferedReader, BufferedWriter
from pathlib import Path

DATAPATH = Path.home() / 'data'
CHUNKSIZE = 1024 * 1024 * 4  # 4 MB
PACKSIZE = 1024 * 1024 * 1024 * 2  # 2 GB


def set_data_path(base_path: str) -> None:
    global DATAPATH
    DATAPATH = Path(base_path)


def get_data_path() -> Path:
    return DATAPATH


def save_chunk(data: bytes, compressed: bool = False) -> tuple[str, str]:
    if compressed:
        data = zlib.compress(data)
    hashstr = hashlib.sha1(data).hexdigest()
    file = get_data_path(
    ) / 'chunks' / hashstr[:2] / hashstr[2:4] / hashstr[4:]
    file.parent.mkdir(parents=True, exist_ok=True)
    with open(file, 'wb') as f:
        f.write(data)
    return str('/'.join(file.parts[-4:])), hashstr


def load_chunk(file: str, compressed: bool = False) -> bytes:
    with open(get_data_path() / file, 'rb') as f:
        data = f.read()
    if compressed:
        data = zlib.decompress(data)
    return data


def load_pack_chunk(pack_reader: BufferedReader, offset: int,
                    size: int) -> bytes:
    pack_reader.seek(offset)
    data = pack_reader.read(size)
    return lzma.decompress(data)


def pack_chunk(pack_writer: BufferedWriter, data: bytes) -> tuple[int, int]:
    offset = pack_writer.tell()
    buf = lzma.compress(data)
    pack_writer.write(buf)
    return offset, len(buf)


def pack_reader(pack: str) -> BufferedReader:
    return open(get_data_path() / 'packs' / pack, 'rb')


def pack_writer() -> BufferedWriter:
    path = get_data_path() / 'packs'
    path.mkdir(parents=True, exist_ok=True)
    for pack in path.glob('*.pack'):
        if pack.stat().st_size < PACKSIZE:
            return open(pack, 'ab'), pack.name
    else:
        pack = path / f'{len(list(path.glob("*.pack"))):06d}.pack'
        return open(pack, 'ab'), pack.name


def delete_chunk(file: str):
    file = get_data_path() / file
    file.unlink()
