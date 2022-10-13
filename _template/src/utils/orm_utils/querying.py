from typing import Optional, Any, TypeVar, Callable

from sqlalchemy.sql import Select

Query = TypeVar('Query', bound=Select)


def add_filter_condition(query: Query, condition: Any | Callable, if_passed: Optional[Any]) -> Select:
    """
    Добавление фильтра к запросу при наличии объекта проверки (!= None)

    :param query: изначальный запрос
    :param condition: условие (можно передать лямбду для lazy evalutaion)
    :param if_passed: объект, по которому выполняется проверка на применение условия
    """
    if if_passed is not None:
        if callable(condition):
            condition = condition()
        query = query.where(condition)
    return query
