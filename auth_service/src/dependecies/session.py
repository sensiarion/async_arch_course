import fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_session import get_db_session

db_session: AsyncSession = fastapi.Depends(get_db_session)
