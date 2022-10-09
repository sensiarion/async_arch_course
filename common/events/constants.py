from enum import Enum


class Events(str, Enum):
    role_changed = 'role_changed'
    user_created = 'user_created'


class CRUDEvents(str, Enum):
    pass


# class Events(BusinessEvents, CRUDEvents, Enum):
#     pass


class Services(str, Enum):
    auth = 'auth'
    tracker = 'tracker'


def get_topic_name(service: Services, event: Events):
    return f'stream_{service.value}_{event.value}'
