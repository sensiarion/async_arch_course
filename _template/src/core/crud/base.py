import logging
import re
from typing import Type, Any, Generic, Callable, Iterable, Optional

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import Select

from core.crud.exceptions import LogicException
from core.crud.filters import AbstractFilter
from core.crud.retrieve import retrieve_object, pagination
from core.crud.types import Entity, Count

from schemas.base import Model

# sorting params
from utils.string_utils import to_snake

SortingFunctionType = Callable[[Select, Entity], str]
SortingElementsType = Iterable[str | tuple[str, SortingFunctionType]]

CollectingKey = str | tuple[str, ...]
CollectingFunctionType = Callable[[Select, Entity, Optional[Any]], Any]
CollectingElementsType = Iterable[CollectingKey | tuple[CollectingKey, CollectingFunctionType]]

# filtering params
FilterValue = Any
FilterFunctionType = Callable[[Select, Entity, FilterValue], Select]
FilterElementsType = Iterable[CollectingKey | tuple[CollectingKey, FilterFunctionType]]


# noinspection PyMethodMayBeStatic
class BaseCrud(Generic[Entity]):
    def __init__(
            self, entity: Type[Entity],
            get_options: list[Any] = None,
            get_multi_options: list[Any] = None,
            sorting_by: SortingElementsType = None,
            filtering_by: SortingElementsType = None,

    ):
        self.get_options = get_options or []
        self.get_multi_options = get_multi_options or []
        self.entity = entity

        self.sort_fields = self._register_sorting(sorting_by) if sorting_by else dict()
        self.filter_fields = self._register_filtering(filtering_by) if filtering_by else dict()

        self.logger = logging.getLogger(to_snake(self.__class__.__name__))

    async def get(
            self,
            session: AsyncSession,
            id: int,
            execution_options: dict[str, Any] = None
    ) -> Entity | None:
        obj = await retrieve_object(
            session,
            self.entity,
            id,
            options=self.get_options,
            execution_options=execution_options
        )

        return obj

    async def get_multi(
            self,
            session: AsyncSession,
            page: int,
            per_page: int,
            with_count: bool = True,
            with_deleted: bool = False,
            sort_by: str = 'id',
            descending: bool = False,
            execution_options: dict[str, Any] = None,
            **filters
    ) -> tuple[list[Entity], Count | None]:
        query: Select = select(self.entity) \
            .options(*self.get_multi_options) \
            .execution_options(**(execution_options or {}))

        try:
            query = self._apply_filtering(query, **filters)
        except (ValueError, TypeError):
            raise LogicException('Failed to apply filter')

        try:
            query = self._apply_sorting(query, sort_by, descending)
        except (ValueError, TypeError):
            raise LogicException('Failed to apply sorting')

        objects, count = await pagination(
            session,
            self.entity,
            page,
            per_page,
            with_count,
            with_deleted,
            query
        )

        return objects, count

    async def _after_values_extracted(
            self,
            session: AsyncSession,
            values: dict,
            is_create: bool = True
    ) -> dict:
        return values

    async def create(
            self,
            session: AsyncSession,
            data: Model,
            *,
            exclude: set[str] = None,
            **kwargs
    ) -> Entity:
        values = data.dict(exclude=exclude)
        values = await self._after_values_extracted(session, values)
        obj = self.entity(**values, **kwargs)
        session.add(obj)
        await session.flush()

        await session.refresh(obj)
        return obj

    async def update(
            self,
            session: AsyncSession,
            obj: Entity,
            data: Model,
            exclude: set[str] = None
    ) -> Entity:
        values = data.dict(exclude=exclude)
        values = await self._after_values_extracted(session, values, is_create=False)
        for attr_name, value in values.items():
            setattr(obj, attr_name, value)

        await session.flush()

        return obj

    def _register_filtering(self, filter_fields: FilterElementsType) -> dict[str, str | FilterFunctionType]:
        """
        Сохраняет перечень доступных фильтров для CRUD'a
        :param filter_fields: перечень фильтров
        :return:
        """
        return self.__collect_key_functions(filter_fields, 'filtering', allow_multiple_keys=True)

    def _parse_keys(
            self, keys: str | tuple[str, ...],
            allow_multiple_keys=False,
            error_name: str = 'sorting',
            name_validation: bool = True
    ) -> CollectingKey:
        """
        Функция для пред обработки передаваемых параметров для функций сортировки и прочего.

        Предназначена для валидации передаваемых ключей. Ключами, как правило, являются поля ORM моделей
        или параметры, которые затем будут использоваться как параметры функций CRUD'а.

        Принимаемые форматы данных:
            * строковое значение (будет валидироваться) по типу названия переменной, т.е. ``user_id`` и подобные
            * поле ORM модели, например ``User.surname``
            * кортеж из вышеперечисленных вариантов (если указан флаг __allow_multiple_keys__), например ``('created_at', 'updated_at')``

        :param keys: ключи для валидации
        :param allow_multiple_keys: допускается ли работа с множественными ключами
        :param error_name: название внешней функции, для более понятной проверки
        :param name_validation: необходимо ли валидировать ключи регуляркой (pythonic names)
        :return: обработанные ключи в стороковом виде (просто строка, если ключ один, либо кортеж)
        """
        if type(keys) != tuple:
            keys = (keys,)

        parsed_keys: list[str] = list()
        for key in keys:
            if name_validation and not re.fullmatch(r'[a-zA-Z0-9_]*', key):
                raise ValueError(f'Key "{key}" is using an incorrect notation. Please write it pythonic')

            parsed_keys.append(key)

        if len(parsed_keys) == 0:
            raise ValueError(f'No keys detected in input param: {keys}')

        if (not allow_multiple_keys) and len(parsed_keys) > 1:
            raise ValueError(
                f'Unable to parse {error_name.lower()} key "{keys}" (multiple keys are prohibited here)'
            )

        return tuple(parsed_keys) if len(parsed_keys) > 1 else parsed_keys[0]

    def __collect_key_functions(
            self, values: CollectingElementsType,
            name: str,
            allow_multiple_keys=False,
    ) -> dict[CollectingKey, str | CollectingFunctionType]:
        registered = dict()
        for param in values:
            if (type(param) == str) or isinstance(param, InstrumentedAttribute):
                # для маппинга по полям модели не поддерживаются множественные ключи
                key = self._parse_keys(param, allow_multiple_keys=False, error_name=name)
                registered[key] = key
            elif type(param) == tuple:
                if len(param) != 2:
                    raise ValueError(
                        f"Registered {name.lower()} function should have sort name "
                        f"and callable sorting function"
                    )

                key, key_callback = param
                key = self._parse_keys(key, allow_multiple_keys=allow_multiple_keys, error_name=name)
                if not callable(key_callback):
                    raise TypeError(f"{name.capitalize()} function should be callable")

                registered[key] = key_callback
            elif isinstance(param, AbstractFilter):
                raise TypeError(
                    f'Unsupported data type "{type(param)}" for {name.lower()}. '
                    f'Maybe, you forgot to call .use() method ?'
                )
            else:
                raise TypeError(f'Unsupported data type "{type(param)}" for {name.lower()}')

        return registered

    def _process_filter_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Приводит передаваемые параметры фильтрации CRUD'a к используемому формату
        :param params: полученные параметры фильтрации
        """
        specified_params = dict()

        for key, value in params.items():
            if value is None:
                continue
            specified_params[to_snake(key)] = value

        return specified_params

    def _apply_default_filtering(self, query: Select, **filter_params: Any) -> Select:
        """
        Вариант фильтрации "по умолчанию", когда не указаны фильтра для CRUD модели (с фильтрацией по параметрам модели).

        :param query: select запрос для сущности, к которому будет применена фильтрация
        :param filter_params: перечень параметров для фильтрации
        """
        for filter_name, filter_value in filter_params.items():
            filter_name = to_snake(filter_name)

            if filter_value is None:
                continue

            if not self.filter_fields:
                if attr := getattr(self.entity, filter_name, None):
                    query = query.where(attr == filter_value)
                else:
                    raise ValueError("Filtering field does not exists")
        return query

    def _apply_user_defined_filtering(self, query: Select, **filter_params: Any) -> Select:
        """
        Вариант фильтрации по указанным пользователем параметрам.

        Пользовательские параметры фильтрации указываются при создании CRUD сущности и могут являться как
        кастомными функциями сортировки, так и ограниченным перечнем для сортировки по полям модели

        :param query: select запрос для сущности, к которому будет применена фильтрация
        :param filter_params: перечень параметров для фильтрации
        """
        for crud_filter_keys, crud_filter in self.filter_fields.items():
            # проверяем совпадение указанных для фильтров ключей с переданными параметрами фильтрации
            crud_filter_keys = crud_filter_keys if type(crud_filter_keys) == tuple else (crud_filter_keys,)
            if not all([key in filter_params for key in crud_filter_keys]):
                continue

            if type(crud_filter) == str:
                filtering_value = filter_params[crud_filter]
                # getattr без параметра по умолчанию, т.к. его существование проверяется при регистрации сортировки
                query = query.where(getattr(self.entity, crud_filter) == filtering_value)
            elif callable(crud_filter):
                try:
                    callback_filter_params = {k: v for k, v in filter_params.items() if k in crud_filter_keys}
                    query = crud_filter(query, self.entity, **callback_filter_params)
                except Exception as e:
                    self.logger.error(
                        f'Unexpected exception from filter function with keys "{crud_filter}"; "{e}"'
                    )
                    raise e

        return query

    def _apply_filtering(self, query: Select, **filter_params: Any) -> Select:
        """
        Применение параметров фильтрации для запроса

        :param query: select запрос для сущности, к которому будет применена фильтрация
        :param filter_params:
        """
        specified_params = self._process_filter_params(filter_params)

        if self.filter_fields:
            query = self._apply_user_defined_filtering(query, **specified_params)
        else:
            query = self._apply_default_filtering(query, **filter_params)

        return query

    def _register_sorting(
            self,
            allowed_sort_fields: SortingElementsType
    ) -> dict[str, str | SortingFunctionType]:
        """
        Сохраняет доступные поля для сортировки в CRUD'e
        :param allowed_sort_fields:
        :return:
        """
        return self.__collect_key_functions(allowed_sort_fields, 'sorting', allow_multiple_keys=False)

    def _apply_sorting(self, query: Select, sort_name: str, descending: bool = False) -> Select:
        """
        Применение функции сортировки к запросу по сконфигурированным функциям сортировки.

        Поведение зависит от того, были ли указан допустимый перечень параметров сортировки
        при создании объекта CRUD'a. Если для параметра ``sorting_by`` были ключи сортировки,
        то **только** эти ключи и будут использоваться для сортировки. **По умолчанию** в качестве ключа
        сортировки может использоваться **любой** аттрибут ORM модели.

        :param query: выполняемый multiple get запрос
        :param sort_name: название ключа для сортировки (будет приведён к snake_case)
        :param descending: использовать ли обратный порядок сортировки
        :return: запрос с применённой сортировкой
        """
        sort_name = to_snake(sort_name)

        order_direction = sqlalchemy.desc if descending else sqlalchemy.asc

        if not self.sort_fields:
            if attr := getattr(self.entity, sort_name, None):
                return query.order_by(order_direction(attr))
            else:
                raise ValueError("Sorting field does not exists")

        sorting_elem = self.sort_fields.get(sort_name)
        if sorting_elem is None:
            raise ValueError("Specified sorting param does not exists")
        elif type(sorting_elem) == str:
            return query.order_by(order_direction(getattr(self.entity, sort_name, None)))
        elif callable(sorting_elem):
            try:
                return query.order_by(order_direction(sorting_elem(query, self.entity)))
            except Exception as e:
                raise Exception(
                    f'Unexpected exception from sorting function called "{sort_name}"; "{e}"'
                ) from e
