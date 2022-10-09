import datetime
import pathlib

import pydantic

from models import MAX_FILENAME_LENGTH
from schemas.base import Model, UidMixin, ListModel
from utils.string_utils import trim_string


class FileCreate(Model):
    name: str = pydantic.Field(..., max_length=MAX_FILENAME_LENGTH)
    path: str

    @pydantic.validator('name')
    def trim_name(cls, val):
        return trim_string(val, MAX_FILENAME_LENGTH)


class FileCreateInner(FileCreate, UidMixin):
    pass


class FileOut(UidMixin):
    name: str
    created_at: datetime.datetime


class FileList(ListModel):
    data: list[UidMixin]
