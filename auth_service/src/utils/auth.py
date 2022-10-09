import datetime
import logging

import fastapi
import jwt
import pydantic

from core.config import Config, config
from schemas.auth import TokenInfo, UserJWTInfo
from utils.time_utils import now


class JWTGenerator:
    """
    Синглтон для работы с jwt
    """
    JWT_SECRET = config.secret
    DEFAULT_ALGORITHM = 'HS256'
    TOKEN_ALIVE_HOURS = datetime.timedelta(hours=config.token_alive_hours)

    logger = logging.getLogger('JWTGenerator')

    TEST_TOKEN = config.test_token

    @classmethod
    def _encode_jwt(cls, data: dict) -> str:
        return jwt.encode(data, key=cls.JWT_SECRET, algorithm=cls.DEFAULT_ALGORITHM)

    @classmethod
    def _decode_jwt(cls, token: str) -> dict:
        return jwt.decode(token, cls.JWT_SECRET, algorithms=[cls.DEFAULT_ALGORITHM])

    @classmethod
    def parse_jwt(cls, token: str) -> TokenInfo | None:
        """
        Получает информацию из jwt токена
        """
        decoded_jwt = None
        try:
            decoded_jwt = cls._decode_jwt(token)
            user_info = TokenInfo(**decoded_jwt)

            return user_info
        except (jwt.InvalidTokenError, jwt.exceptions.InvalidSignatureError) as e:
            cls.logger.debug(f'Failed to decode token: "{token}"; {str(e)}')
        except pydantic.ValidationError as e:
            cls.logger.debug(f'Got some unparsed dict from token "{decoded_jwt}"; {str(e)}')

        return None

    @classmethod
    def create_jwt(cls, user: UserJWTInfo) -> str:
        """
        Создаёт jwt токен из данных пользователя
        :param user:
        :return:
        """
        created_at = now()
        expired_at = created_at + cls.TOKEN_ALIVE_HOURS

        token_info = TokenInfo(
            sub=user.id,
            role_id=user.role_id,
            exp=expired_at,
            iat=created_at
        )

        token = cls._encode_jwt(token_info.dict(by_alias=True))

        return token

    @classmethod
    def validate_jwt(cls, token: str) -> UserJWTInfo:
        """
        Проверяет jwt токен на валидность и возвращает информацию о пользователе

        :raises NotAuthorized
        """
        user_info = cls.parse_jwt(token)

        err = fastapi.HTTPException(401, detail='Wrong JWT')
        if not user_info:
            raise err

        expired_at = datetime.datetime.fromtimestamp(user_info.token_expired_at, tz=datetime.timezone.utc) \
            .replace(tzinfo=None)
        current_time = datetime.datetime.utcnow()
        if expired_at < current_time:
            raise err

        return UserJWTInfo(id=user_info.sub, role_id=user_info.role_id)
