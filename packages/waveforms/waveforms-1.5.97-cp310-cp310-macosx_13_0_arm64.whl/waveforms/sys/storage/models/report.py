from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, LargeBinary,
                        String, Text)
from sqlalchemy.orm import relationship

from ..file import load_object as _load_object
from ..file import save_object as _save_object
from .association import (record_reports, report_comments, report_tags,
                          sample_reports)
from .base import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    ctime = Column(DateTime, default=datetime.utcnow)
    mtime = Column(DateTime, default=datetime.utcnow)
    atime = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))

    category = Column(String)
    title = Column(String)
    content = Column(Text)
    file = Column(String)
    key = Column(String)
    task_hash = Column(LargeBinary(32))

    user = relationship("User")
    samples = relationship("Sample",
                           secondary=sample_reports,
                           back_populates="reports")

    records = relationship('Record',
                           secondary=record_reports,
                           back_populates='reports')

    tags = relationship('Tag', secondary=report_tags, back_populates='reports')
    comments = relationship('Comment', secondary=report_comments)
    _parameters = relationship('ReportParameters')

    @property
    def obj(self):
        self.atime = datetime.utcnow()
        return _load_object(self.file)

    @obj.setter
    def obj(self, data):
        self.file, _ = _save_object(data)

    def parameters(self):
        return {p.key: p.value for p in self._parameters}

    def set_parameter(self, **kwds):
        for key, value in kwds.items():
            for p in self._parameters:
                if p.key == key:
                    p.parameter.value = value
                    break
            else:
                p = Parameter()
                p.value = value
                rp = ReportParameters(key=key)
                rp.parameter = p
                self._parameters.append(rp)
