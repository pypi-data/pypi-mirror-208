from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .association import (comment_tags, record_tags, report_tags, sample_tags,
                          snapshot_tags)
from .base import Base


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    text = Column(String, unique=True)

    comments = relationship('Comment',
                            secondary=comment_tags,
                            back_populates='tags')
    records = relationship('Record',
                           secondary=record_tags,
                           back_populates='tags')
    reports = relationship('Report',
                           secondary=report_tags,
                           back_populates='tags')
    samples = relationship('Sample',
                           secondary=sample_tags,
                           back_populates='tags')
    snapshots = relationship('Snapshot',
                             secondary=snapshot_tags,
                             back_populates='tags')

    def __init__(self, text) -> None:
        super().__init__()
        self.text = text

    def __repr__(self):
        return f"Tag('{self.text}')"
