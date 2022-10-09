import datetime

import pydantic

from core.constants import ROLES
from schemas.base import Model, IdMixin
from schemas.users import UserOut
from utils.time_utils import timestamp_to_unix


class UserJWTInfo(Model):
    id: str
    role_id: int


class TokenInfo(pydantic.BaseModel):
    """
    Дополнительная информация содержащаяся в JWT токене
    """
    sub: str | None
    role_id: int
    token_expired_at: float | datetime.datetime = pydantic.Field(..., alias='exp')
    token_created_at: float | datetime.datetime = pydantic.Field(..., alias='iat')

    @pydantic.validator('token_expired_at', pre=True)
    def validate_token_expired_at(cls, value):
        return timestamp_to_unix(value)

    @pydantic.validator('token_created_at', pre=True)
    def validate_token_created_at(cls, value):
        return timestamp_to_unix(value)


class LoginOut(Model):
    token: str = pydantic.Field(..., description='JWT токен пользователя')
    user: UserOut


system_user = UserJWTInfo(id='1ad5ddae-03d4-49ce-9fe0-84a5a2db1980', role_id=ROLES.ADMIN.value)
