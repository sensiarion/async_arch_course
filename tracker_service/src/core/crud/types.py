from typing import TypeVar, NewType

Entity = TypeVar('Entity')

Id = int | str

Count = NewType('Count', int)
