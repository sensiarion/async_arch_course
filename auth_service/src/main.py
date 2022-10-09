import fastapi
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from core.config import config
from routes.auth import auth_router
from routes.exceptions import apply_exception_handlers
from routes.middlewares import LimitUploadSize
from routes.users import user_router

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
app.include_router(auth_router, prefix='/auth')
app.include_router(user_router, prefix='/users')


@app.on_event('startup')
async def startup():
    pass
