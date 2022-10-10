import random

import fastapi
import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.constants import ROLES, STATUSES
from core.crud.base import BaseCrud
from models import Task, User
from schemas.tasks import TaskCreateIn
from utils.orm_utils.orm_utils import load_property


class TaskCrud(BaseCrud):
    async def create(
            self,
            session: AsyncSession,
            data: TaskCreateIn,
            *,
            exclude: set[str] = None,
            **kwargs
    ) -> Task:
        assign_user = await self._choose_user_for_assign(session)
        task = await super().create(
            session,
            data,
            exclude=exclude,
            status_id=STATUSES.opened.value,
            assigned_by=assign_user.id
        )
        await self.set_price(session, task)

        await session.flush()
        await load_property(session, task, {'assigned', 'status'})

        return task

    async def _choose_user_for_assign(self, session: AsyncSession) -> User:
        query = select(User).where(
            User.role_id.notin_([ROLES.MANAGER.value, ROLES.ADMIN.value])
        ).order_by(sqlalchemy.func.random()).limit(1)
        user = await session.scalar(query)

        if not user:
            raise fastapi.HTTPException(503, detail='No users found')
        return user

    async def assign_user(self, session: AsyncSession, task: Task):
        user = await self._choose_user_for_assign(session)
        task.assigned_by = user.id
        task.assigned = user

    async def set_price(self, session: AsyncSession, task: Task):
        assign_price = random.randint(-20, -10)
        complete_price = random.randint(20, 40)
        task.assign_price = assign_price
        task.complete_price = complete_price


task_crud = TaskCrud(
    Task,
    get_options=[joinedload(Task.status), selectinload(Task.status_changes), joinedload(Task.assigned)],
    get_multi_options=[joinedload(Task.status), joinedload(Task.assigned)]
)
