from sqlalchemy import Column, ForeignKey, Table

from .base import Base

user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', ForeignKey('users.id'), primary_key=True),
                   Column('role_id', ForeignKey('roles.id'), primary_key=True))

record_reports = Table(
    'record_reports', Base.metadata,
    Column('record_id', ForeignKey('records.id'), primary_key=True),
    Column('report_id', ForeignKey('reports.id'), primary_key=True))

comment_tags = Table(
    'comment_tags', Base.metadata,
    Column('comment_id', ForeignKey('comments.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True))

snapshot_tags = Table(
    'snapshot_tags', Base.metadata,
    Column('snapshot_id', ForeignKey('snapshots.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True))

record_tags = Table(
    'record_tags', Base.metadata,
    Column('record_id', ForeignKey('records.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True))

report_tags = Table(
    'report_tags', Base.metadata,
    Column('report_id', ForeignKey('reports.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True))

sample_tags = Table(
    'sample_tags', Base.metadata,
    Column('sample_id', ForeignKey('samples.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True))

sample_reports = Table(
    'sample_reports', Base.metadata,
    Column('sample_id', ForeignKey('samples.id'), primary_key=True),
    Column('report_id', ForeignKey('reports.id'), primary_key=True))

sample_records = Table(
    'sample_records', Base.metadata,
    Column('sample_id', ForeignKey('samples.id'), primary_key=True),
    Column('record_id', ForeignKey('records.id'), primary_key=True))

sample_comments = Table(
    'sample_comments', Base.metadata,
    Column('sample_id', ForeignKey('samples.id'), primary_key=True),
    Column('comment_id', ForeignKey('comments.id'), primary_key=True))

sample_transfer_comments = Table(
    'sample_transfer_comments', Base.metadata,
    Column('transfer_id', ForeignKey('sample_transfer.id'), primary_key=True),
    Column('comment_id', ForeignKey('comments.id'), primary_key=True))

report_comments = Table(
    'report_comments', Base.metadata,
    Column('report_id', ForeignKey('reports.id'), primary_key=True),
    Column('comment_id', ForeignKey('comments.id'), primary_key=True))

record_comments = Table(
    'record_comments', Base.metadata,
    Column('record_id', ForeignKey('records.id'), primary_key=True),
    Column('comment_id', ForeignKey('comments.id'), primary_key=True))
