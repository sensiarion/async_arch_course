import datetime
from typing import List, Optional

import pydantic

from core.constants import ROLES
from schemas.base import Model, ListModel
from schemas.roles import RoleBare
from utils.passwords import generate_password_hash


class UserUpdateIn(Model):
    login: Optional[str] = pydantic.Field(min_length=4, max_length=256)
    password: Optional[str] = pydantic.Field(min_length=6, max_length=256)
    email: Optional[pydantic.EmailStr]
    last_name: Optional[str] = pydantic.Field(min_length=1, max_length=256)
    first_name: Optional[str] = pydantic.Field(min_length=1, max_length=256)

    @pydantic.validator('login')
    def validate_login(cls, v):
        if not v.isascii():
            raise ValueError("Логин может состоять только из символов латиницы")
        for letter in v:
            if letter.isspace():
                raise ValueError("В логине не должно быть пробелов")
        return v

    @pydantic.validator('password')
    def hash_password(cls, val: str):
        if val:
            password_hash = generate_password_hash(val)
            return password_hash


class RegisterUserIn(Model):
    login: str = pydantic.Field(min_length=4, max_length=256)
    password: str = pydantic.Field(min_length=6, max_length=256)
    email: pydantic.EmailStr
    last_name: str = pydantic.Field(min_length=1, max_length=256)
    first_name: str = pydantic.Field(min_length=1, max_length=256)

    role_id: int = pydantic.Field(ROLES.USER.value, const=True, example=ROLES.USER.value)

    @pydantic.validator('login')
    def validate_login(cls, v: str):
        if not v.isascii():
            raise ValueError("Логин может состоять только из символов латиницы")
        for letter in v:
            if letter.isspace():
                raise ValueError("В логине не должно быть пробелов")
        return v

    @pydantic.validator('password')
    def hash_password(cls, val: str):
        if val:
            password_hash = generate_password_hash(val)
            return password_hash


class UserOut(Model):
    id: str
    login: str
    last_name: str
    first_name: str
    role_id: int
    email: Optional[str]

    role: RoleBare

    class Config(Model.Config):
        orm_mode = True


class UserLoginOut(Model):
    user: UserOut
    token: str


class UserListOut(ListModel):
    data: List[UserOut]
