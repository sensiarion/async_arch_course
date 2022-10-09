import fastapi
from starlette.middleware.cors import CORSMiddleware

from core.config import config
from routes.exceptions import apply_exception_handlers
from routes.middlewares import LimitUploadSize
from routes.statuses import status_router
from routes.tasks import task_router

app = fastapi.FastAPI(title='async arch')
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
app.include_router(status_router, prefix='/statuses')
app.include_router(task_router, prefix='/tasks')


@app.on_event('startup')
async def startup():
    pass
