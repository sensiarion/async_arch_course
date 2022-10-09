from typing import TypeVar, Optional, Any

SetType = TypeVar('SetType', bound=set)


def add_to_set(set_: Optional[SetType], value: Any) -> SetType:
    if set_ is None:
        set_ = set()
    set_.add(value)

    return set_
