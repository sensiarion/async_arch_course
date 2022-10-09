import logging

import aiomisc.entrypoint
import sqlalchemy

from common.events.constants import Events, get_topic_name, Services
from common.events.messages.base_schema import EventMessage
from common.kafka_utils.config import kafka_base_config
from common.kafka_utils.consumer import AbstractKafkaConsumer
from common.kafka_utils.shared import KafkaConfig
from internals.users import user_crud
from schemas.users import UserOut
from utils.db_session import db_session_manager


class UserCreatedConsumer(AbstractKafkaConsumer):
    async def on_startup(self):
        pass

    async def process(self, message: EventMessage):
        assert message.event_name == Events.user_created.value, 'wrong message passed'
        data = message.payload['user']
        async with db_session_manager() as session:
            try:
                user = await user_crud.create(
                    session,
                    UserOut(
                        id=data['id'],
                        login=data['login'],
                        last_name=data['last_name'],
                        first_name=data['first_name'],
                        role_id=data['role_id'],
                        role_name=data['role']['name'],
                        email=data['email'],
                    )
                )
                self.logger.info(f'User {user.id} created')
            except sqlalchemy.exc.IntegrityError:
                self.logger.info(f"User {data['id']} duplicated. skipping")
                await session.rollback()


if __name__ == '__main__':
    config = KafkaConfig(
        group_id='tracker_user_created_consumer',
        bootstrap_servers=kafka_base_config.kafka_bootstrap_servers,
        input_topic=get_topic_name(Services.auth, Events.user_created)
    )
    consumer = UserCreatedConsumer(connection_config=config)
    with aiomisc.entrypoint(consumer, log_level=logging.INFO) as loop:
        loop.run_forever()
