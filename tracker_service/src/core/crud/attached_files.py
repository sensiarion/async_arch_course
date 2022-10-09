from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.retrieve import retrieve_batch, refresh_collection
from core.crud.types import Entity
from models import Base, File
from schemas.base import Model
from utils.orm_utils.orm_utils import load_property


class AttachedFilesMixin:
    @staticmethod
    async def update_files(
            session: AsyncSession,
            obj: Entity,
            data: Model,
            secondary_relation_name: str,
            relation: Type[Base],
            entity_id_column_name: str,
            relation_name: str = 'files'
    ):
        await retrieve_batch(session, File, {i.id for i in getattr(data, relation_name)})
        await load_property(session, obj, {secondary_relation_name, relation_name})

        def create_secondary(**params):
            secondary_params = {'file_id': params['id'], entity_id_column_name: obj.id}
            return relation(**secondary_params)

        val = await refresh_collection(
            session,
            obj.files,
            data.files,
            relation,
            secondary_relation_base_obj_name='file',
            creation_func=create_secondary
        )
        setattr(obj, relation_name, val)

        await session.flush()
        session.expire(obj, {relation_name})
