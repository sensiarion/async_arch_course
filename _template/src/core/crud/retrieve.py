from typing import Type, List, Any, Collection, Iterable, Callable, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from core.crud.exceptions import ObjectNotExists
from core.crud.types import Entity, Id, Count
from models import Base
from schemas.base import Model


async def retrieve_object(
        session: AsyncSession,
        entity: Type[Entity],
        id_: Id,
        options: List[Any] = None,
        execution_options: dict[str, Any] = None
) -> Entity:
    """
    Load object from database and ensure it exists

    :param session: current session
    :param entity: entity (ORM) class
    :param id_: object identifier (primary key)
    :param options: query load optins like joinedload or subqueryload
    :raise ObjectNotExists: if not found
    :return:
    """
    query: Select = select(entity).where(entity.id == id_)
    if options:
        query = query.options(*options)
    if execution_options:
        query = query.execution_options(**execution_options)
    obj = await session.scalar(query)
    if obj is None:
        raise ObjectNotExists(f'Object {entity.__name__} not found in database', id_)

    return obj


async def pagination(
        session: AsyncSession,
        ModelClass: Type[Entity],
        page: int = 1,
        rows_per_page: int | None = 25,
        with_count: bool = True,
        with_deleted: bool = False,
        query: Select = None
) -> tuple[list[Entity], Count]:
    """
    Выполняет запрос с пагинацией.

    Явно указывать запрос им
    :param query: запрос по которому будет выполнен запрос
    :param page: страница
    :param rows_per_page: кол-во элементов на 1 странице выдачи
    :param with_deleted: игнорирования удалённых записей использующих SoftDeleteMixin
    :param ModelClass: класс для возвращаемых значений. Нужен для typehints
    :return: Список значений и предельное их кол-во
    """
    if query is None:
        query = select(ModelClass)

    if with_deleted:
        query = query.execution_options(include_deleted=True)

    if with_count:
        rows_number = (await session.execute(select(func.count('*')).select_from(query))).scalar_one()
    else:
        rows_number = None

    if rows_per_page:
        query = query.limit(rows_per_page)

    final_query = query.offset((page - 1) * (rows_per_page or 0))

    values = (await session.execute(final_query)).scalars().unique().all()
    return values, rows_number


Existing = TypeVar('Existing', bound=Base)
Arrived = TypeVar('Arrived', bound=Model)


async def refresh_collection(
        session: AsyncSession,
        existing_objects: Iterable[Existing],
        arrived_objects: Iterable[Arrived],
        creation_class: Type[Existing],
        secondary_relation_base_obj_name: str,
        exclude_on_creation: set[str] = None,
        equal_by: str | Callable[[Existing, Arrived], bool] = 'id',
        creation_func: Callable = None,

        **creation_params: Any,

) -> List[Existing]:
    """
    Актуализация списка значений исходя из прибывших

    **Обязательно наличие поля** `id`

    :param session:
    :param existing_objects:
    :param arrived_objects:
    :param equal_by:
    :param creation_class:
    :param exclude_on_creation:
    :param creation_params:
    :param secondary_relation_base_obj_name: имя настоящей сущности у secondary объекта
    :return:
    """
    if exclude_on_creation is None:
        exclude_on_creation = set()

    if type(equal_by) == str:
        equal_by_arg = equal_by
        equal_by = lambda e, a: getattr(e, equal_by_arg) == getattr(a, equal_by_arg, None)
    new_values = []

    matched_objects = []

    for arrived in arrived_objects:
        matched = list(filter(lambda existing: equal_by(existing, arrived), existing_objects))
        if matched:
            matched_objects.append(matched[0])
        else:
            new_values.append(arrived)

    if creation_func is None:
        values = [
            creation_class(**new.dict(exclude=exclude_on_creation), **creation_params)
            for new in new_values
        ]
    else:
        values = [
            creation_func(**new.dict(exclude=exclude_on_creation), **creation_params) for new in
            new_values
        ]

    session.add_all(values)
    await session.flush()

    def _new_files(session):
        return [getattr(i, secondary_relation_base_obj_name) for i in values]

    entity_values = await session.run_sync(_new_files)

    return [*matched_objects, *entity_values]


RetrieveType = TypeVar('RetrieveType', bound=Base)


def check_missing_entities(ids: Iterable[int], objects: List[Base], model: Base):
    """
    Проверка на наличие несуществующих записей бд между запрашиваемыми идентификаторами и данными из БД

    :raises: ObjectNotExists при отсутствии 1 или более сущностей в БД
    """
    if len(set(ids)) != len(objects):
        retrieving_ids = set(ids)
        existing_ids = {i.id for i in objects}

        diff = retrieving_ids.symmetric_difference(existing_ids)

        raise ObjectNotExists(
            message=f'Objects with ids {", ".join(map(str, diff))} not exists',
            ids=list(diff)
        )


async def retrieve_batch(
        session: AsyncSession,
        model: Type[RetrieveType],
        ids: Collection[int | str],
        query: Select = None,
        attr_name: str = 'id'
) -> dict[int | str, RetrieveType]:
    """
    Запрашивает набор объектов по идентификатором из базы данных

    :param query: запрос для получения сущностей
    :param model: запрашиваемая модель
    :param ids: список идентификаторов объектов для данной модели
    :param attr_name: поле, по которому будут запрашиваться сущности. Подразумевается уникальность по данному полю
    :raises ObjectNotExists при отсутствии одной из запрашиваемых записей
    :return: словарь из пар идентификатор:объект
    """

    query = (select(model) if query is None else query).where(getattr(model, attr_name).in_(ids))

    objects = (await session.execute(query)).scalars().all()

    check_missing_entities(ids, objects, model)

    return {getattr(obj, attr_name): obj for obj in objects}
