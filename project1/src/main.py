import fastapi
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from core.config import config
from routes.exceptions import apply_exception_handlers
from routes.files import file_router
from routes.middlewares import LimitUploadSize

from utils.db_session import db_session_manager

app = fastapi.FastAPI(title='tradediary')
app.add_middleware(LimitUploadSize, max_upload_size=config.max_file_size)
apply_exception_handlers(app)

if not config.cors_policy_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
        allow_credentials=True,
    )
app.include_router(file_router, prefix='/files')


@app.on_event('startup')
async def startup():
    pass
