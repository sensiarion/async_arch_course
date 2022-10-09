import asyncio
import logging
from abc import abstractmethod
from typing import Optional, TypeVar, Type

import aiomisc
import orjson
import pydantic
from aiokafka import AIOKafkaConsumer, ConsumerRecord

from common.events.messages.base_schema import EventMessage
from .shared import KafkaConfig

InputType = TypeVar('InputType', bound=EventMessage)


class AbstractKafkaConsumer(aiomisc.Service):
    """
    Абстрактный класс для реализации сервиса consumer'a для kafka

    Если в настройках соединения указан **group_id**, то from_topic_begin не сработает,
     поэтому его желательно выставлять в **True**.
    Подобное поведение наиболее желательно (в PRODUCTION среде должен быть выставлен group_id и
    from_topic_begin не будет действовать,
    в режиме отладки, когда group_id=None, можно будет получать все записи для обработки)
    """
    InputModel: Type[InputType] = EventMessage

    on_error_wait = 0.2

    def __init__(self, connection_config: KafkaConfig, from_topic_begin=False, **kwargs):
        """
        Создание экземляра consumer'a. У класса должно быть определено свойство InputModel,
         для сериализации поступающих данных.

        Если в настройках соединения указан **group_id**, то from_topic_begin не сработает,
         поэтому его желательно выставлять в **True**.
        Подобное поведение наиболее желательно (в PRODUCTION среде должен быть выставлен group_id и
        from_topic_begin не будет действовать,
        в режиме отладки, когда group_id=None, можно будет получать все записи для обработки)

        :param connection_config: конфигурация для работы с kafka; output_topic необязателен
        :param from_topic_begin: обрабатывать данные с начала очереди
        """
        aiomisc.Service.__init__(self, **kwargs)
        if not self.InputModel:
            raise TypeError("You should specify InputModel type")

        self.from_topic_begin = from_topic_begin
        self.kafka_config = connection_config
        if not self.kafka_config.input_topic:
            raise ValueError("Kafka input topic should be specified in config")

        self.logger = logging.getLogger(self.__class__.__name__)

        self.consumer: Optional[AIOKafkaConsumer] = None

    def _create_consumer(self) -> AIOKafkaConsumer:
        return AIOKafkaConsumer(
            self.kafka_config.input_topic,
            loop=self.loop,
            bootstrap_servers=self.kafka_config.bootstrap_servers,
            group_id=self.kafka_config.group_id,
            value_deserializer=orjson.loads,
            auto_offset_reset="earliest" if self.from_topic_begin else 'latest',
            enable_auto_commit=False
        )

    @abstractmethod
    async def on_startup(self):
        """
        Необязательный к реализации хук, который выполняется до запуска consumer'a
        """
        pass

    @abstractmethod
    async def process(self, message: InputModel):
        """
        Обработка полученного сообщения.

        Обработка выполняется после сериализации к указанному виду сообщения.
        """
        pass

    async def start(self, trigger_start=True):
        if self.consumer is None:
            self.consumer = self._create_consumer()
        else:
            raise Exception("Only single run is allowed for consumer")

        await self.on_startup()
        self.logger.info(f'started up {self.kafka_config.input_topic}')

        await self.consumer.start()
        self.logger.info(f'start consuming {self.kafka_config.input_topic}')

        if trigger_start:
            self.start_event.set()

        try:
            async for msg in self.consumer:
                await self._consume(msg)
                await self.consumer.commit()

        finally:
            self.logger.info('stopping')
            await self.consumer.stop()
            self.logger.info('consume stopped')

    async def stop(self, exception: Exception = None):
        if self.consumer is not None:
            await self.consumer.stop()

    async def _consume(self, msg: ConsumerRecord):
        err_extra_info = {
            'raw_message': msg.value, 'topic': msg.topic,
            'partition': msg.partition, 'offset': msg.offset
        }

        self.logger.debug(
            f'consumed on: topic={msg.topic}, partition={msg.partition}, offset={msg.offset},'
            f' key={msg.key} timestamp={msg.timestamp}; value: {msg.value}'
        )

        try:
            record = self.InputModel(**msg.value)
            await self.process(record)
        except pydantic.ValidationError:
            self.logger.error(f'unable to parse kafka message', extra=err_extra_info)
            await asyncio.sleep(self.on_error_wait)
        except Exception as e:
            self.logger.error(f'Error processing message: {e}', exc_info=True, extra=err_extra_info)
            await asyncio.sleep(self.on_error_wait)
