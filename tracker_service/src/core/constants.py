from enum import IntEnum


class ROLES(IntEnum):
    ADMIN = 1
    MANAGER = 2
    USER = 3


class STATUSES(IntEnum):
    opened = 1
    closed = 2
