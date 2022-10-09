import pydantic

from schemas.base import Model


class ErrorSchema(Model):
    detail: str = pydantic.Field(..., example='Error message eng')
    context: dict
