from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from utils.orm_utils.softdelete import SoftDeleteMixin
from sqlalchemy import Column, Integer, text, Float, Text, String, DateTime, ForeignKey, Boolean

from models.base import Base
from utils.time_utils import now

MAX_FILENAME_LENGTH = 512


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256))


class User(Base, SoftDeleteMixin):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    login = Column(String(64))
    password = Column(Text)
    email = Column(String(256))
    role_id = Column(Integer, ForeignKey('roles.id'))
    first_name = Column(String(256))
    last_name = Column(String(256))

    role = relationship('Role')
