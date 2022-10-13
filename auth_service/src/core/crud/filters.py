"""
Функции фильтрации, которые могут использоваться в CRUD фильтрах
"""
import abc
from abc import ABC
from contextlib import suppress
from typing import Any, Tuple, Union, Type

from sqlalchemy import func, select
from sqlalchemy.sql import Select, Subquery, visitors

from core.crud.types import Entity


class AbstractFilter(abc.ABC):
    """
    Сигнатура функции фильтрации.
    """

    def __init__(self, required_fields: str):
        """
        Конструктор для указания изначальных параметров функции фильтрации.

        Допускается переопределять конструктор, обозначая перечень полей на уровне всего класса

        :param required_fields: перечень параметров, необходимых для фильтрации
        """
        self.required_fields = required_fields

    @abc.abstractmethod
    def __call__(self, query: Select, model: Entity, **filter_params: Any) -> Select:
        """
        Вызов функции фильтрации

        В filter_params будут переданы те параметры, которые вы указали в перечне required_fields.
        Функция будет вызвана только в том случае, если все обозначенные параметры фильтрации были переданы
        при вызове endpoint'a (все параметры ``is not None``)

        :param query: запрос, к которому будет применена фильтрация
        :param model: ORM объект, для которого необходимо осуществить фильтрация
        :param filter_params: запрашиваемые параметры фильтрации
        :return: модифицированный запрос с условиями фильтрации
        """
        raise NotImplementedError()

    def use(self):
        """
        Функция, с помощью которой можно указать инстанс функции фильтрации для использования в CRUD'e
        :return:
        """
        return self.required_fields, self


class IlikeFilter(AbstractFilter):
    """
    Фильтр с ``case insensitive`` поиском по указанному полю
    """

    def __init__(self, field_name: str):
        """
        :param field_name: названия поля модели
        """
        super().__init__(field_name)

    def __call__(self, query: Select, model: Entity, **filter_params: Any) -> Select:
        try:
            attr = getattr(model, self.required_fields)
        except AttributeError as e:
            raise ValueError(
                f'specified attribute {self.required_fields} is not exists on model {model}'
            ) from e
        query = query.where(attr.ilike(f'%{filter_params[self.required_fields].lower()}%'))

        return query


class IncludeFilter(AbstractFilter):
    """
    Фильтр не по прямому сравнению, а по вхождению во множество через sql оператор ``IN``

    Передаваемый параметр должен быть списком
    """

    def __init__(self, field_name: str, alias: str = None):
        self.field_name = field_name
        super().__init__(alias if alias else field_name)

    def __call__(self, query: Select, model: Entity, **filter_params: Any) -> Select:
        param = filter_params[self.required_fields]
        if type(param) != list:
            raise TypeError(f"Parameter {self.required_fields} should be a list for IN comparison")
        try:
            attr = getattr(model, self.field_name)
        except AttributeError as e:
            raise ValueError(
                f'specified attribute {self.field_name} is not exists on model {model}'
            ) from e
        query = query.where(attr.in_(param))
        return query


class LevenshteinFilter(AbstractFilter):
    """
    Фильтр по расстоянию Левенштейна.

    На самом деле **это не фильтр, а сортировка** но всё же.

    При использовании данного фильтра, к запросу будет применена сортировка по похожести текстового поля.
    Важный нюанс – т.к. это сортировка, то данный критерий сортировки будет являться первичными, а все иные
    указанные сортировки будут являться вторичными.


    **Работает для строк не более 255 символов**. Учитывайте это при создании фильтра
    """

    def __init__(self, field_name: str, model: Entity):
        """
        :param field_name: названия поля модели
        """
        super().__init__(field_name)
        self.model = model

        column_attr = getattr(model, self.required_fields)
        column_length = column_attr.property.columns[0].type.length
        if (column_length is None) or column_length >= 256:
            raise ValueError(
                f"Unable to implement Levenshtein filter. It can be use only with"
                f" text fields, that have length < 256"
            )

    def __call__(self, query: Select, model: Entity, **filter_params: Any) -> Select:
        value = filter_params[self.required_fields]

        if len(value) > 255:
            raise ValueError("Levenshtein filter can't work with string, having more than 255 characters")

        source = func.lower(getattr(model, self.required_fields))
        # По-умолчанию левенштейн за каждый символ который необходимо вставить, изменить,
        # или удалить из строки-источника (первый аргумент) увелиичивает расстояние до нее на 1
        # что собственно делает невозможным адекватный поиск по подстроке.
        # Например: расстояние между 'FFFFFFFFFFFF' и 'F' будет 11,
        # а не 0 как нужно для корректного поиска по подстроке
        # необходимо явно указать что удаление в строке-источнике
        # не приводит к увеличению расстояния
        levenshtein_call = func.levenshtein(source, value.lower(), 1, 0, 1)
        return query.order_by(levenshtein_call)
