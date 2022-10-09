import fastapi

# TODO
from schemas.auth import UserJWTInfo


async def user_dep(reqeust: fastapi.Request) -> UserJWTInfo:
    return UserJWTInfo(id=-1)


user_info: UserJWTInfo = fastapi.Depends(user_dep)
