from typing import Iterable

from core.crud.types import Id


class ObjectNotExists(Exception):
    def __init__(self, message: str, ids: Iterable[Id] | Id = None):
        self.message = message
        self.ids = ids

    def __repr__(self):
        return f'{self.__class__.__name__}<message={self.message}, ids={self.ids}>'

    def __str__(self):
        return self.message


class ObjectAlreadyExists(Exception):
    def __init__(self, message: str):
        self.message = message

    def __repr__(self):
        return f'{self.__class__.__name__}<message={self.message}>'

    def __str__(self):
        return self.message


class LogicException(Exception):
    """
    Ошибка в бизнес логике приложения
    """

    def __init__(self, message: str):
        self.message = message
