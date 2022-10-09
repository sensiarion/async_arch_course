import logging
from typing import Any, Iterable

import aiomisc.service.periodic
from sqlalchemy import select

from dependecies import db_session
from common.events.constants import Services, Events

from common.events.messages.base_schema import EventMessage

from events import event_producer
from kafka_utils.consumer import AbstractKafkaConsumer
from kafka_utils.producer import EventKafkaProducer
from models import Event
from utils.db_session import db_session_manager
from utils.time_utils import now


class BatchEventStreamer(aiomisc.service.periodic.PeriodicService):
    BATCH_SIZE = 200
    logger = logging.getLogger('batch-event-streamer')

    def __init__(self, event_producer: EventKafkaProducer, *args, **kwargs):
        self.event_producer = event_producer

        super().__init__(**kwargs)

    async def callback(self) -> Any:
        async with db_session_manager() as session:
            query = select(Event).where(Event.sent_at == None).order_by(Event.timestamp).limit(
                self.BATCH_SIZE
            )
            values: Iterable[Event] = await session.scalars(query)

            for event in values:
                await self.event_producer.send_message(
                    Services.auth, Events(event.name), EventMessage(
                        uuid=event.id,
                        event_name=Events(event.name),
                        service=Services.auth,
                        payload=event.payload,
                        timestamp=event.timestamp
                    )
                )
                self.logger.info(f'event: {event.id} sent')
                event.sent_at = now()



if __name__ == '__main__':
    with aiomisc.entrypoint(
            event_producer,
            BatchEventStreamer(event_producer, interval=5),
            log_level=logging.INFO
    ) as loop:
        loop.run_forever()
