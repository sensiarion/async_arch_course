import fastapi

# TODO
from fastapi import security, Depends

from core.config import config
from schemas.auth import UserJWTInfo, system_user
from utils.auth import JWTGenerator


async def user_dep(
        token: security.HTTPAuthorizationCredentials = Depends(
            security.HTTPBearer(bearerFormat='Bearer')
        )
) -> UserJWTInfo:
    """
    """
    if config.test_token and token.credentials == config.test_token:
        return system_user
    data = JWTGenerator.validate_jwt(token.credentials)

    return data


user_info: UserJWTInfo = fastapi.Depends(user_dep)
