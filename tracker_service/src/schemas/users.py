from schemas.base import Model


class UserOut(Model):
    id: str
    login: str
    email: str
    role_id: int
    role_name: str
    first_name: str
    last_name: str
