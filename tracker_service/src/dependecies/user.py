import logging

import fastapi
import httpx
from cachetools import TTLCache
from fastapi import Depends, security

from core.config import config
from schemas.auth import UserJWTInfo, UserValidate

# вместо тысячи редисов
users_cache = TTLCache(maxsize=1024, ttl=60 * 60)

logger = logging.getLogger('auth-dep')


async def user_dep(
        token: security.HTTPAuthorizationCredentials = Depends(
            security.HTTPBearer(bearerFormat='Bearer')
        )
) -> UserValidate:
    if user := users_cache.get(token.credentials):
        return user

    async with httpx.AsyncClient() as client:
        response = await client.post(
            config.auth_service_token_validate_url,
            params={'token': token.credentials}
        )
        if response.status_code == 401:
            raise fastapi.HTTPException(401, detail='Incorrect JWT token')
        elif response.status_code == 200:
            user_data = UserValidate(**response.json())
            users_cache[token.credentials] = user_data
            return user_data
        else:
            logger.error(
                f'Failed to validate jwt token on auth server. '
                f'Got: {response.status_code}; data: {response.text}'
            )
            raise fastapi.HTTPException(503, detail='Failed to validate authorization')


user_info: UserJWTInfo = fastapi.Depends(user_dep)
