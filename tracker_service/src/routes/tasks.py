import fastapi

from dependecies import db_session
from dependecies.user import user_info
from internals.tasks import task_crud
from schemas.tasks import TaskListOut, TaskOutFull, TaskCreateIn

task_router = fastapi.APIRouter(tags=['tasks'])


@task_router.get('', name='get multi', response_model=TaskListOut)
async def get_task_list(
        page: int = fastapi.Query(1, description='page'),
        per_page: int = fastapi.Query(25, description='elements per page', le=100),
        session=db_session,
        author=user_info
) -> TaskListOut:
    tasks, count = await task_crud.get_multi(session, page, per_page)

    # noinspection PyUnusedLocal
    def _create_list_model(session):
        return TaskListOut(data=tasks, page=page, per_page=per_page, total=count)

    serialized = await session.run_sync(_create_list_model)
    return serialized


@task_router.get('/{id}', response_model=TaskOutFull)
async def get_task(id: int = fastapi.Path(...), session=db_session, author=user_info) -> TaskOutFull:
    task = await task_crud.get(session, id)
    return await TaskOutFull.from_orm_async(session, task)


@task_router.post('', response_model=TaskOutFull)
async def create_task(data: TaskCreateIn, session=db_session, author=user_info) -> TaskOutFull:
    task = await task_crud.create(session, data, created_by=author)

    return await TaskOutFull.from_orm_async(session, task)


# @task_router.put('/{id}', response_model=TaskOutFull)
# async def update_task(
#         data: TaskCreateIn,
#         id: int = fastapi.Path(...),
#         session=db_session,
#         author=user_info
# ) -> TaskOutFull:
#     task = await task_crud.get(session, id)
#
#     updated = await task_crud.update(session, task, data)
#
#     return await TaskOutFull.from_orm_async(session, updated)
#
#
# @task_router.delete('/{id}', response_model=TaskOutFull)
# async def delete_task(id: int = fastapi.Path(...), session=db_session, author=user_info) -> TaskOutFull:
#     task = await task_crud.get(session, id)
#     data = await TaskOutFull.from_orm_async(session, task)
#
#     task.delete()
#     await session.flush()
#
#     return data
