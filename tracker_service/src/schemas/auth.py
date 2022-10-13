from schemas.base import Model, IdMixin


class UserJWTInfo(IdMixin):
    commission: float = 0


system_user = UserJWTInfo(id=-1)
