import fastapi

from dependecies import db_session
from dependecies.user import user_info
from internals.statuses import status_crud
from schemas.statuses import StatusBare, StatusListOut

status_router = fastapi.APIRouter(tags=['statuss'])


@status_router.get('', name='get multi', response_model=StatusListOut)
async def get_status_list(
        page: int = fastapi.Query(1, description='page'),
        per_page: int = fastapi.Query(25, description='elements per page', le=100),
        session=db_session,
        author=user_info
) -> StatusListOut:
    statuss, count = await status_crud.get_multi(session, page, per_page)

    # noinspection PyUnusedLocal
    def _create_list_model(session):
        return StatusListOut(data=statuss, page=page, per_page=per_page, total=count)

    serialized = await session.run_sync(_create_list_model)
    return serialized


@status_router.get('/{id}', response_model=StatusBare)
async def get_status(id: int = fastapi.Path(...), session=db_session, author=user_info) -> StatusBare:
    status = await status_crud.get(session, id)
    return await StatusBare.from_orm_async(session, status)
