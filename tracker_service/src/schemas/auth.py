from schemas.base import Model


class UserJWTInfo(Model):
    id: str
    role_id: int


class UserValidate(Model):
    id: str
    login: str
    last_name: str
    first_name: str
    role_id: int
    email: str | None

    class Config(Model.Config):
        orm_mode = True
