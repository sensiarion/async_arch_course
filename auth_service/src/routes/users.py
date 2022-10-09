import fastapi

from core.constants import ROLES
from core.crud.exceptions import LogicException
from core.crud.retrieve import retrieve_object
from dependecies import db_session
from dependecies.auth import user_info
from common.events.constants import Events
from internals.events import create_event
from internals.users import user_crud
from models import Role
from schemas.roles import RoleBare
from schemas.users import UserListOut, UserOut, UserUpdateIn

user_router = fastapi.APIRouter(tags=['users'])


@user_router.get('', name='get multi', response_model=UserListOut)
async def get_user_list(
        page: int = fastapi.Query(1, description='page'),
        per_page: int = fastapi.Query(25, description='elements per page', le=100),
        session=db_session,
        author=user_info
) -> UserListOut:
    users, count = await user_crud.get_multi(session, page, per_page)

    # noinspection PyUnusedLocal
    def _create_list_model(session):
        return UserListOut(data=users, page=page, per_page=per_page, total=count)

    serialized = await session.run_sync(_create_list_model)
    return serialized


@user_router.get('/{id}', response_model=UserOut)
async def get_user(id: int = fastapi.Path(...), session=db_session, author=user_info) -> UserOut:
    user = await user_crud.get(session, id)
    return await UserOut.from_orm_async(session, user)


@user_router.put('/{id}', response_model=UserOut)
async def update_user(
        data: UserUpdateIn,
        id: str = fastapi.Path(...),
        session=db_session,
        author=user_info
) -> UserOut:
    if author.id != id:
        raise LogicException('Пользователь может обновлять только личную информацию')
    user = await user_crud.get(session, id)

    updated = await user_crud.update(session, user, data)

    return await UserOut.from_orm_async(session, updated)


@user_router.put('/{id}/role', response_model=UserOut)
async def change_role(
        id: str = fastapi.Path(...),
        new_role_id: int = fastapi.Body(..., alias='newRoleId'),
        session=db_session,
        author=user_info,
) -> UserOut:
    if author.role_id != ROLES.ADMIN.value:
        raise LogicException("Недостаточно прав")

    try:
        ROLES(new_role_id)
    except ValueError:
        raise LogicException("Указанная роль не существует")

    user = await user_crud.get(session, id)
    old_role = await retrieve_object(session, Role, user.role_id)
    new_role = await retrieve_object(session, Role, new_role_id)
    user.role_id = new_role_id

    create_event(
        session, Events.role_changed, {
            'user': UserOut.from_orm(user).dict(),
            'old_role': RoleBare.from_orm(old_role).dict(),
            'new_role': RoleBare.from_orm(new_role).dict()
        }
    )

    await session.flush()
    return await UserOut.from_orm_async(session, user)


@user_router.delete('/{id}', response_model=UserOut)
async def delete_user(id: int = fastapi.Path(...), session=db_session, author=user_info) -> UserOut:
    if author.role_id != ROLES.ADMIN.value:
        raise LogicException("Недостаточно прав")

    user = await user_crud.get(session, id)
    data = await UserOut.from_orm_async(session, user)

    user.delete()
    await session.flush()

    return data
