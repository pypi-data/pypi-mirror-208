import time
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer,
                        LargeBinary, String)
from sqlalchemy.orm import relationship

from ..file import load_object as _load_object
from ..file import save_object as _save_object
from .association import (record_comments, record_reports, record_tags,
                          sample_records)
from .base import Base


class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    ctime = Column(DateTime, default=datetime.utcnow)
    mtime = Column(DateTime, default=datetime.utcnow)
    atime = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    parent_id = Column(Integer, ForeignKey('records.id'))
    cell_id = Column(Integer, ForeignKey('cells.id'))

    app = Column(String)
    file = Column(String)
    key = Column(String)
    config = Column(JSON)
    task_hash = Column(LargeBinary(32))

    parent = relationship("Record",
                          remote_side=[id],
                          back_populates="children")
    children = relationship("Record",
                            remote_side=[parent_id],
                            back_populates="parent")

    user = relationship("User")
    samples = relationship("Sample",
                           secondary=sample_records,
                           back_populates="records")
    cell = relationship("Cell")

    reports = relationship('Report',
                           secondary=record_reports,
                           back_populates='records')
    tags = relationship('Tag', secondary=record_tags, back_populates='records')
    comments = relationship('Comment', secondary=record_comments)

    def __init__(self,
                 file: str = None,
                 key: Optional[str] = None,
                 dims: list[str] = [],
                 vars: list[str] = [],
                 dims_units: list[str] = [],
                 vars_units: list[str] = [],
                 coords: Optional[dict] = None):
        self.file = file
        if key is None:
            self.key = '/Data' + time.strftime("%Y%m%d%H%M%S")
        else:
            self.key = key
        self.dims = dims
        self.vars = vars
        self.dims_units = dims_units
        self.vars_units = vars_units
        self.coords = coords

        self._buff = ([], [])

    @property
    def data(self):
        self.atime = datetime.utcnow()
        ret = _load_object(self.file)
        if isinstance(ret, dict) and 'meta' in ret:
            ret['meta']['id'] = self.id
        return ret

    @data.setter
    def data(self, data):
        self.file, _ = _save_object(data)
