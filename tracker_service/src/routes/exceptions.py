import fastapi
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.crud.exceptions import ObjectNotExists, ObjectAlreadyExists, LogicException
from schemas.base import ErrResponse


def apply_exception_handlers(app: fastapi.FastAPI):
    @app.exception_handler(ObjectNotExists)
    async def object_not_found(request: Request, e: ObjectNotExists) -> JSONResponse:
        return JSONResponse(ErrResponse(detail=f'Objects with ids {e.ids} not found').dict(), status_code=404)

    @app.exception_handler(ObjectAlreadyExists)
    async def object_already_exists(request: Request, e: ObjectAlreadyExists) -> JSONResponse:
        return JSONResponse(ErrResponse(detail=e.message).dict(), status_code=409)

    @app.exception_handler(LogicException)
    async def logic_exception(request: Request, e: LogicException) -> JSONResponse:
        return JSONResponse(ErrResponse(detail=e.message).dict(), status_code=400)
