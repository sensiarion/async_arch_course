import datetime
import uuid
from typing import Type, Any, TypeVar, Optional

import pydantic
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from utils.string_utils import to_camel

ModelType = TypeVar('ModelType', bound=BaseModel)


class Model(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True

    @classmethod
    async def from_orm_async(cls: Type['ModelType'], session: AsyncSession, obj: Any) -> 'ModelType':
        serialized = await session.run_sync(lambda session: cls.from_orm(obj))

        return serialized


class IdMixin(Model):
    id: int


class CreatedTimestampMixin(Model):
    created_at: Optional[datetime.date]


class UidMixin(Model):
    id: str = pydantic.Field(..., example=str(uuid.uuid4()))


class ListModel(Model):
    data: list[IdMixin]
    page: int
    per_page: int | None
    total: int = pydantic.Field(None, description='total count of objects with specified filters/params')


class StatusResponse(Model):
    detail: str = 'ok'


class ErrResponse(Model):
    detail: str
    context: dict = pydantic.Field(default_factory=dict)
