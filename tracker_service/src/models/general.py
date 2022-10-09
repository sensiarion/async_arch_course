from sqlalchemy import Column, Integer, text, Text, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from models.base import Base
from utils.orm_utils.softdelete import SoftDeleteMixin
from utils.time_utils import now

MAX_FILENAME_LENGTH = 512


class User(Base, SoftDeleteMixin):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)
    login = Column(String(64))
    email = Column(String(256))
    role_id = Column(Integer)
    role_name = Column(Text)
    first_name = Column(String(256))
    last_name = Column(String(256))

    created_at = Column(DateTime, default=now(), nullable=False)


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    name = Column(String(512))
    description = Column(Text)
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    assign_price = Column(Integer, nullable=True)
    complete_price = Column(Integer, nullable=True)
    assigned_by = Column(UUID, ForeignKey('users.id'), nullable=False)

    created_at = Column(DateTime, default=now(), nullable=False)

    status = relationship('Status')
    assigned = relationship('User')
    status_changes = relationship('StatusChanges', uselist=True)


class Status(Base):
    __tablename__ = 'statuses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256))


class StatusChanges(Base):
    __tablename__ = 'status_changes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    task_id = Column(UUID, ForeignKey('tasks.id'), nullable=False)
    created_at = Column(DateTime, default=now(), nullable=False)


class Event(Base):
    __tablename__ = 'stream_events'
    id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    name = Column(Text)
    payload = Column(JSONB)
    timestamp = Column(DateTime, default=now)
    sent_at = Column(DateTime)
