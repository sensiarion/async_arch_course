import datetime

import pydantic

from common.events.constants import Events, Services


class EventMessage(pydantic.BaseModel):
    uuid: str
    event_name: Events
    service: Services
    payload: dict
    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.utcnow())

    class Config:
        use_enum_values = True
