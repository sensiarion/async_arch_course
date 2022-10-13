import hashlib
import pathlib
import uuid

import aiofiles
import aiofiles.os
from fastapi import UploadFile

from core.config import config
from core.crud.exceptions import ObjectNotExists
from core.crud.owned import CreatedByCrud
from models import File
from schemas.auth import UserJWTInfo


class FileHandler:
    DEFAULT_EXTENSION = 'txt'
    CHUNK_SIZE = 4096

    @classmethod
    def get_user_directory(cls, user: UserJWTInfo) -> pathlib.Path:
        dir_name = hashlib.md5(str(user.id).encode('utf-8')).hexdigest()
        user_dir = config.file_path / dir_name

        return user_dir

    @classmethod
    async def get_file_path(cls, relative_path: str):
        full_path = config.file_path / relative_path

        if not (await aiofiles.os.path.exists(full_path)):
            raise ObjectNotExists(f'Unable to found file')

        return full_path

    @classmethod
    def parse_filename(cls, data: UploadFile, user: UserJWTInfo) -> tuple[pathlib.Path, str]:
        user_dir = cls.get_user_directory(user)

        filename_parts = data.filename.split('.')
        if (not filename_parts) or len(filename_parts) == 1:
            filename_parts = filename_parts + [cls.DEFAULT_EXTENSION]

        ext = filename_parts[-1]
        orig_name = '.'.join(filename_parts[:-1])
        filename = f'{uuid.uuid4()}.{ext}'

        filepath = user_dir / filename

        return filepath, orig_name

    @classmethod
    async def save_file(
            cls,
            data: UploadFile,
            user: UserJWTInfo,
            path=None,
            orig_name=None
    ) -> tuple[pathlib.Path, str]:
        if not path and not orig_name:
            path, orig_name = cls.parse_filename(data, user)
        if not (await aiofiles.os.path.exists(path.parent)):
            await aiofiles.os.mkdir(path.parent)

        async with aiofiles.open(path.absolute(), 'wb') as result_file:
            while chunk := await data.read(cls.CHUNK_SIZE):
                await result_file.write(chunk)

        return path, orig_name


class FileCrud(CreatedByCrud):
    pass


file_crud = FileCrud(File)
