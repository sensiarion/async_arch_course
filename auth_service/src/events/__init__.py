from common.kafka_utils.config import kafka_base_config
from common.kafka_utils.producer import EventKafkaProducer
from common.kafka_utils.shared import KafkaConfig

connection_config = KafkaConfig(
    input_topic=None,
    group_id='auth_service',
    bootstrap_servers=kafka_base_config.kafka_bootstrap_servers
)
event_producer = EventKafkaProducer(connection_config)
