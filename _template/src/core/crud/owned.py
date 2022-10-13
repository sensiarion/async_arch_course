from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.base import BaseCrud
from core.crud.types import Entity
from schemas.auth import UserJWTInfo
from schemas.base import Model


class CreatedByCrud(BaseCrud):
    """
    Crud, marking all values as create by specific user
    """

    user_id: ContextVar[int] = ContextVar('user_id', default=None)

    async def _after_values_extracted(
            self,
            session: AsyncSession,
            values: dict,
            is_create: bool = True
    ) -> dict:
        if is_create:
            values['created_by'] = self.user_id.get()
        return values

    # noinspection PyMethodOverriding
    async def create(
            self,
            session: AsyncSession,
            data: Model,
            created_by: UserJWTInfo,
            *,
            exclude: set[str] = None,
            **kwargs
    ) -> Entity:
        self.user_id.set(created_by.id)
        return await super().create(session, data, exclude=exclude, **kwargs)
