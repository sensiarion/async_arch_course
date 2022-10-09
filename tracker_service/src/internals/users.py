from core.crud.base import BaseCrud
from models import User


class UserCrud(BaseCrud):
    pass


user_crud = UserCrud(User)
