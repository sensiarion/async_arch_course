import uuid

import aiofiles.os
import fastapi
from fastapi import UploadFile
from starlette.background import BackgroundTask, BackgroundTasks

from core.config import config
from core.crud.exceptions import ObjectNotExists
from dependecies import db_session
from dependecies.user import user_info
from internals.files import file_crud, FileHandler
from schemas.files import FileOut, FileCreate, FileList
from utils.time_utils import now

file_router = fastapi.APIRouter(tags=['files'])

if config.is_testing:
    @file_router.get('', name='get multi', response_model=FileList)
    async def get_files_list(
            page: int = fastapi.Query(1, description='page'),
            per_page: int | None = fastapi.Query(None, description='elements per page'),
            session=db_session,
            author=user_info
    ) -> FileList:
        books, count = await file_crud.get_multi(session, page, per_page)

        # noinspection PyUnusedLocal
        def _create_list_model(session):
            return FileList(data=books, page=page, per_page=per_page, total=count)

        serialized = await session.run_sync(_create_list_model)
        return serialized


@file_router.get('/{id}')
async def get_file(
        id: str = fastapi.Path(..., example=str(uuid.uuid4())),
        session=db_session,
        author=user_info
):
    file = await file_crud.get(session, id)

    file_path = await FileHandler.get_file_path(file.path)

    extension = file.path.split('.')[-1]
    return fastapi.responses.FileResponse(file_path, filename=f'{file.name}.{extension}')


@file_router.get('/{id}/info', response_model=FileOut)
async def get_file_info(
        id: str = fastapi.Path(..., example=str(uuid.uuid4())),
        session=db_session,
        author=user_info
) -> FileOut:
    file = await file_crud.get(session, id)
    return await FileOut.from_orm_async(session, file)


@file_router.post('/upload', response_model=FileOut)
async def upload_file(file: UploadFile, session=db_session, author=user_info) -> FileOut:
    filepath, orig_name = await FileHandler.save_file(file, author)

    res = await file_crud.create(
        session,
        FileCreate(name=orig_name, path=str(filepath.relative_to(config.file_path))),
        created_by=author,
        created_at=now()
    )

    return FileOut.from_orm(res)


@file_router.put('/{id}', response_model=FileOut)
async def update_file(
        data: FileCreate,
        id: str = fastapi.Path(..., example=str(uuid.uuid4())),
        session=db_session,
        author=user_info
) -> FileOut:
    file = await file_crud.get(session, id)

    updated = await file_crud.update(session, file, data)

    return await FileOut.from_orm_async(session, updated)


@file_router.delete('/{id}', response_model=FileOut)
async def delete_file(
        tasks: BackgroundTasks,
        id: str = fastapi.Path(..., example=str(uuid.uuid4())),
        session=db_session,
        author=user_info,

) -> FileOut:
    file = await file_crud.get(session, id)
    data = await FileOut.from_orm_async(session, file)

    file.delete()
    await session.flush()
    return data
