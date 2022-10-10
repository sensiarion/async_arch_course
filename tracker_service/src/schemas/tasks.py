import datetime

import pydantic

from schemas.base import Model, UidMixin, ListModel
from schemas.statuses import StatusBare, StatusChangeBare


class TaskCreateIn(Model):
    name: str = pydantic.Field(min_length=1, max_length=512)
    description: str = pydantic.Field(min_length=1, max_length=10 * 1024)


class TaskBare(TaskCreateIn, UidMixin):
    status_id: int
    assign_price: int
    complete_price: int
    assigned_by: str
    created_at: datetime.datetime


class TaskOut(TaskBare):
    status: StatusBare


class TaskOutFull(TaskOut):
    status_changes: list[StatusChangeBare]


class TaskListOut(ListModel):
    data: list[TaskOut]
