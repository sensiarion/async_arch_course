from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.base import BaseCrud
from core.crud.types import Entity
from models import Status
from schemas.base import Model


class StatusCrud(BaseCrud):
    async def create(
            self,
            session: AsyncSession,
            data: Model,
            *,
            exclude: set[str] = None,
            **kwargs
    ) -> Entity:
        raise NotImplementedError("Not allowed")

    async def update(
            self,
            session: AsyncSession,
            obj: Entity,
            data: Model,
            exclude: set[str] = None
    ) -> Entity:
        raise NotImplementedError("Not allowed")


status_crud = StatusCrud(Status)

