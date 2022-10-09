from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import Query, Session, ORMExecuteState, with_loader_criteria


class SoftDeleteMixin:
    deleted_at = sa.Column(sa.DateTime(timezone=False), nullable=True)

    def delete(self, deleted_at: datetime = None):
        self.deleted_at = deleted_at or datetime.now()

    def restore(self):
        self.deleted_at = None


@event.listens_for(Session, 'do_orm_execute')
def before_compile(execute_state: ORMExecuteState):
    include_deleted = execute_state.execution_options.get('include_deleted', False)
    if include_deleted:
        return

    if not execute_state.is_relationship_load and execute_state.all_mappers:
        for mapper in execute_state.all_mappers:
            if mapper and issubclass(mapper.class_, SoftDeleteMixin):
                execute_state.statement = execute_state.statement.where(mapper.entity.deleted_at.is_(None))

    else:
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True
            )
        )
