import fastapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.exceptions import LogicException
from dependecies import db_session
from internals.users import user_crud
from models import User
from schemas.users import UserOut, RegisterUserIn, UserLoginOut
from utils.auth import JWTGenerator
from utils.passwords import verify_password

auth_router = fastapi.APIRouter()


@auth_router.post(
    '/register', response_model=UserOut, status_code=201,
    responses={409: {'description': 'User with specified login or email already exists'}}
)
async def register(
        register_info: RegisterUserIn,
        session: AsyncSession = db_session
) -> UserOut:
    """
    Регистрация в системе
    """
    query = user_crud.get_user_by_login_query(register_info.login, register_info.email).limit(1)
    user = await session.scalar(query)
    if user:
        raise fastapi.HTTPException(409, detail='Такой пользователь уже существует')

    user = await user_crud.create(session, register_info)

    return await UserOut.from_orm_async(session, user)


@auth_router.post(
    '/login', response_model=UserLoginOut,
    responses={401: {'description': 'Wrong creds'}}
)
async def login(
        login: str = fastapi.Query(min_length=4, max_length=256),
        password: str = fastapi.Query(min_length=6, max_length=256),
        session: AsyncSession = db_session
) -> UserLoginOut:
    query = user_crud.get_user_by_login_query(login, login)
    user = await session.scalar(query)
    if user is None:
        raise fastapi.HTTPException(401, detail='Неверный логин или пароль')
    if not verify_password(password, user.password):
        raise fastapi.HTTPException(401, detail='Неверный логин или пароль')

    token = JWTGenerator.create_jwt(user)

    return UserLoginOut(user=user, token=token)


@auth_router.post(
    '/validate', response_model=UserOut,
    responses={401: {'description': 'Wrong creds'}}
)
async def validate(
        token: str = fastapi.Query(min_length=3),
        session: AsyncSession = db_session
) -> UserOut:
    data = JWTGenerator.validate_jwt(token)
    user = await user_crud.get(session, data.id)
    return await UserOut.from_orm_async(session, user)
