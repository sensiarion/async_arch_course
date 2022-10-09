from sqlalchemy import select
from sqlalchemy.orm import joinedload

from core.crud.base import BaseCrud
from models import User


class UserCrud(BaseCrud):

    @classmethod
    def get_user_by_login_query(cls, login: str, email: str):
        return select(User).where(
            User.login.ilike(login) | User.email.ilike(email)
        ).options(joinedload(User.role))


user_crud = UserCrud(User, get_options=[joinedload(User.role)])
