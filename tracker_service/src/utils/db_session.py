import contextlib
from typing import AsyncGenerator, Callable, AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from core.config import config


def async_session_factory(
        async_connection_string,
        **engine_params
) -> tuple[AsyncGenerator[AsyncSession, None], Callable[[], AsyncContextManager[AsyncSession]], AsyncEngine]:
    """
    Функция для создания асинхронной фабрики соединений с бд

    :param async_connection_string: connection url начинающийся с postgresql+asyncpg
    :param engine_params: параметры для AsyncEngine (настройки пула соединений)
    :return: генератор для использования в fastapi.Depends, контекстный менеджер
             бд для использования в любом ином месте, AsyncEngine для низкоуровнего взаимодействия
    """
    async_engine_default_params = {
        'poolclass': NullPool
    }

    async_engine_default_params.update(engine_params)

    engine = create_async_engine(async_connection_string, **async_engine_default_params)
    # noinspection PyTypeChecker
    maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async def get_async_session() -> AsyncSession:
        try:
            sess: AsyncSession = maker()
            yield sess
        except Exception as e:
            await sess.rollback()
            raise e
        finally:
            await sess.commit()
            await sess.close()

    return get_async_session, contextlib.asynccontextmanager(get_async_session), engine


get_db_session, db_session_manager, db_engine = async_session_factory(config.async_db_conn_str)
