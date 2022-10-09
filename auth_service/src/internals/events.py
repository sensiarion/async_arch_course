import logging

from common.events.constants import Events
from sqlalchemy.ext.asyncio import AsyncSession

from models import Event

logger = logging.getLogger('event-creating')


def create_event(session: AsyncSession, name: Events, payload: dict) -> Event:
    event = Event(name=name.value, payload=payload)
    session.add(event)
    logger.info(f'event {event.name} created')
    return event
