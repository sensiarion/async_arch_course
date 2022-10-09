from pydantic import BaseSettings


class KafkaBaseConfig(BaseSettings):
    kafka_bootstrap_servers: str


kafka_base_config = KafkaBaseConfig()
