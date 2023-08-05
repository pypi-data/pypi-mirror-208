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
from waveforms.dicttree import NOTSET

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


class Edge(Base):
    __tablename__ = 'edges'

    left_id = Column(ForeignKey('nodes.id'), primary_key=True)
    right_id = Column(ForeignKey('nodes.id'), primary_key=True)
    key = Column(String(50), primary_key=True)

    def __repr__(self):
        return f'Edge(key={self.key})'


class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    value_id = Column(ForeignKey('values.id'), nullable=True)
    is_tree = Column(Boolean, default=False)

    value = relationship('Value')
    children = relationship("Edge",
                            foreign_keys=[Edge.left_id],
                            backref="parent")
    parents = relationship("Edge",
                           foreign_keys=[Edge.right_id],
                           backref="child")


class Snapshot(Base):
    __tablename__ = 'snapshots'

    id = Column(Integer, primary_key=True)
    ctime = Column(DateTime, nullable=False, default=datetime.utcnow)
    root_id = Column(ForeignKey('nodes.id'))
    previous_id = Column(Integer, ForeignKey('snapshots.id'))

    followers = relationship("Snapshot",
                             backref=backref('previous', remote_side=[id]))

    root = relationship('Node')

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


def _setitem(root: Union[Node, int], key: str, node: Union[Node, int]):
    edge = Edge()
    edge.key = key
    if isinstance(root, Node):
        if root.id is None:
            edge.parent = root
        else:
            edge.left_id = root.id
    else:
        edge.left_id = root.id
    if isinstance(node, Node):
        if node.id is None:
            edge.child = node
        else:
            edge.right_id = node.id
    else:
        edge.right_id = node.id


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


def _create_node(session: Session, value: dict = {}) -> Node:
    root = Node()
    if not isinstance(value, dict):
        root.is_tree = False
        _set_node_value(root, _create_value(session, value))
        return root

    root.is_tree = True

    for k, v in value.items():
        _setitem(root, k, _create_node(session, v))
    return root


def _query(session: Session, nodes: list[Node],
           keys: list[str]) -> tuple[Node, list[str]]:
    try:
        node = session.query(Node).join(Edge, Node.id == Edge.right_id).filter(
            nodes[-1].id == Edge.left_id).filter(Edge.key == keys[0]).one()
        return _query(session, [*nodes, node], keys[1:])
    except Exception as e:
        return nodes, keys


def _update(session: Session, root: Node, updates: dict) -> Node:
    if not updates:
        return root

    if not isinstance(updates, dict):
        return _create_node(session, updates)

    new_root = Node()
    new_root.is_tree = True

    updated_keys = set()
    for edge in root.children:
        updated_keys.add(edge.key)
        if edge.key in updates:
            if updates[edge.key] is NOTSET:
                continue
            elif isinstance(updates[edge.key], dict):
                node = _update(session, edge.child, updates[edge.key])
            else:
                node = _create_node(session, updates[edge.key])
        else:
            node = edge.child
        _setitem(new_root, edge.key, node)

    for k in set(updates.keys()) - updated_keys:
        _setitem(new_root, k, _create_node(session, updates[k]))

    return new_root


def _export_node(node: Node) -> dict:
    if node.is_tree:
        return {a.key: _export_node(a.child) for a in node.children}
    else:
        return node.value.value


def create(session: Session, value: Union[dict, Node] = None) -> Snapshot:
    snapshot = Snapshot()
    if value is None:
        value = {}
    if isinstance(value, Node):
        snapshot.root = value
    else:
        snapshot.root = _create_node(session, value)
    session.add(snapshot)
    session.commit()
    return snapshot


def query(session: Session, snapshot: Snapshot, key: str):
    nodes, keys = _query(session, [snapshot.root], key.split('.'))
    if keys:
        return None
    else:
        return _export_node(nodes[-1])


def update(session: Session, snapshot: Snapshot, updates: dict) -> Snapshot:
    root = _update(session, snapshot.root, updates)
    snapshot = Snapshot(previous_id=snapshot.id)
    snapshot.root = root
    session.add(snapshot)
    session.commit()
    return snapshot


def export(session: Session, snapshot: Union[Snapshot, int]):
    if isinstance(snapshot, int):
        snapshot = session.get(Snapshot, snapshot)
    return _export_node(snapshot.root)
