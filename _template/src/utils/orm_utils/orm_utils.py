from sqlalchemy.ext.asyncio import AsyncSession


async def load_property(session: AsyncSession, obj, attrs: set[str]):
    # noinspection PyUnusedLocal
    def get_attrs(session):
        for attr in attrs:
            getattr(obj, attr)

    await session.run_sync(get_attrs)
