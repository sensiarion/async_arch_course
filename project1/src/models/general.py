from sqlalchemy.dialects.postgresql import UUID

from utils.orm_utils.softdelete import SoftDeleteMixin
from sqlalchemy import Column, Integer, text, Float, Text, String, DateTime, ForeignKey, Boolean

from models.base import Base
from utils.time_utils import now

MAX_FILENAME_LENGTH = 512


class File(Base, SoftDeleteMixin):
    __tablename__ = 'files'

    id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    name = Column(String(MAX_FILENAME_LENGTH))
    path = Column(Text)
    is_public = Column(Boolean, server_default='false', nullable=False)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=now)
