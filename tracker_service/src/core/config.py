import pathlib
from urllib import parse

import pydantic
from pydantic import BaseSettings

project_dir_name = (pathlib.Path(__file__).parent.parent.parent).name


class DBConfig(BaseSettings):
    """
    Параметры для подключения к БД
    """
    db_name: str
    db_password: str
    db_host: str
    db_port: str
    db_user: str

    # noinspection PyUnboundLocalVariable
    async_db_conn_str: str = ''

    @pydantic.validator('async_db_conn_str', always=True, check_fields=False)
    def build_url(cls, value, values):
        db_name, db_password = values['db_name'], values['db_password']
        db_host, db_port, db_user = values['db_host'], values['db_port'], values['db_user']

        return f'postgresql+asyncpg://{db_user}:{parse.quote(db_password)}@{db_host}:{db_port}/{db_name}'


class Config(DBConfig):
    host: str = '127.0.0.1'
    port: int

    auth_service_token_validate_url: str
    max_file_size: int = 50_000_000  # ~50mb with default
    file_path: pathlib.Path = pathlib.Path('../files')

    cors_policy_enabled: bool = 'True'
    is_testing: bool = False

    class Config:
        env_prefix = f'{project_dir_name.upper()}_'


config = Config()
