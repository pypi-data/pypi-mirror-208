import gzip
import hashlib
import pathlib
import pickle
from datetime import datetime
from functools import cached_property
from typing import Any, Union

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
                        LargeBinary, String, create_engine, event)
from sqlalchemy.orm import (backref, declarative_base, relationship,
                            sessionmaker)
from sqlalchemy.orm.session import Session
from waveforms.dicttree import NOTSET, flattenDict, foldDict

Base = declarative_base()

CHUNCKSIZE = 256


def get_data_path():
    return pathlib.Path.home() / 'test_data'


def _get_buff_fname(data: bytes) -> str:
    hashstr = hashlib.sha1(data).hexdigest()
    file = '/'.join([hashstr[:2], hashstr[2:4], hashstr[4:]])
    return file.encode('utf-8')


def _save_buff(data, fname=None):
    if fname is None:
        fname = _get_buff_fname(data).decode('utf-8')
    file = get_data_path() / 'objects' / fname
    file.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(file, 'wb') as f:
        f.write(data)
    return file


def _save_object(data, fname=None):
    data = pickle.dumps(data)
    return _save_buff(data, fname)


def _load_buff(file: str) -> bytes:
    with gzip.open(get_data_path() / 'objects' / file, 'rb') as f:
        data = f.read()
    return data


def _load_object(file: str) -> bytes:
    with gzip.open(get_data_path() / 'objects' / file, 'rb') as f:
        data = pickle.load(f)
    return data


class Value(Base):
    __tablename__ = 'values'

    id = Column(Integer, primary_key=True)
    size = Column(Integer, nullable=False)
    chunck = Column(LargeBinary(CHUNCKSIZE), nullable=False, unique=False)

    _buffer = None

    @cached_property
    def value(self):
        if self.chunck is None:
            return None
        if self.size <= CHUNCKSIZE:
            return pickle.loads(self.chunck[:self.size])
        else:
            if self._buffer is not None:
                return pickle.loads(self._buffer)
            else:
                return _load_object(self.chunck[:42].decode())

    def set_value(self, value):
        buff = pickle.dumps(value)
        self.size = len(buff)
        if self.size <= CHUNCKSIZE:
            self.chunck[:self.size] = buff
        else:
            self._buffer = buff
            self.chunck[:42] = _get_buff_fname(buff)


@event.listens_for(Value, "before_insert", propagate=True)
def save_buffer(mapper, connection, value):
    if value._buffer is not None:
        _save_buff(value._buffer)


class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    key = Column(String(512))
    value_id = Column(ForeignKey('values.id'), nullable=True)
    snapshot_id = Column(ForeignKey('snapshots.id'), nullable=True)

    value = relationship('Value')
    snapshot = relationship('Snapshot', back_populates='nodes')


class Snapshot(Base):
    __tablename__ = 'snapshots'

    id = Column(Integer, primary_key=True)
    ctime = Column(DateTime, nullable=False, default=datetime.utcnow)
    previous_id = Column(Integer, ForeignKey('snapshots.id'))

    followers = relationship("Snapshot",
                             backref=backref('previous', remote_side=[id]))
    nodes = relationship('Node', back_populates='snapshot')

    def __repr__(self):
        return f'Snapshot(id={self.id}, previous_id={self.previous_id})'


def create_tables(engine, tables_only=False):
    Base.metadata.create_all(engine)
    if tables_only:
        return
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        session.commit()
    except:
        session.rollback()


def _create_value(session: Session, value: Any):
    value_obj = Value(size=0, chunck=bytearray(CHUNCKSIZE))
    value_obj.set_value(value)
    exist_value_id = session.query(
        Value.id).filter(Value.size == value_obj.size).filter(
            Value.chunck == value_obj.chunck).one_or_none()
    if exist_value_id is None:
        return value_obj
    else:
        return exist_value_id[0]


def _set_node_value(node: Node, value: Union[Value, int]):
    if isinstance(value, Value):
        if value.id is None:
            node.value = value
        else:
            node.value_id = value.id
    else:
        node.value_id = value


def update(session: Session, snapshot: Snapshot, updates: dict) -> Node:
    if not updates:
        return snapshot

    updates = flattenDict(updates)
    deletes = set()
    for k, v in updates.items():
        if v is NOTSET:
            deletes.add(k)
    new_snapshot = Snapshot(previous_id=snapshot.id)

    for node in snapshot.nodes:
        if node.key not in updates and node.key not in deletes and not any(
                node.key.startswith(d + '.') for d in deletes):
            n = Node(key=node.key, value_id=node.value_id)
            new_snapshot.nodes.append(n)
    for k, v in updates.items():
        if v is NOTSET:
            continue
        else:
            n = Node(key=k, snapshot=new_snapshot)
            _set_node_value(n, _create_value(session, v))
            new_snapshot.nodes.append(n)

    session.add(new_snapshot)
    session.commit()

    return new_snapshot


def query(session: Session, snapshot: Snapshot, key: str):
    key = key.replace('*', '%')
    nodes = session.query(Node).filter(Node.snapshot_id == snapshot.id).filter(
        Node.key.like(key)).all()
    return foldDict({node.key: node.value.value for node in nodes})


def create(session: Session, value: Union[dict, Node] = None) -> Snapshot:
    updates = flattenDict(value)
    snapshot = Snapshot()

    for k, v in updates.items():
        if v is NOTSET:
            continue
        else:
            n = Node(key=k, snapshot=snapshot)
            _set_node_value(n, _create_value(session, v))
            snapshot.nodes.append(n)

    session.add(snapshot)
    session.commit()

    return snapshot


def export(session: Session, snapshot: Union[Snapshot, int]):
    return foldDict({node.key: node.value.value for node in snapshot.nodes})
