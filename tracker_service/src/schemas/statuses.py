import datetime

from schemas.base import Model, ListModel


class StatusBare(Model):
    id: str
    name: str


class StatusChangeBare(Model):
    status_id: int
    task_id: str
    created_at: datetime.datetime


class StatusListOut(ListModel):
    data: list[StatusBare]
