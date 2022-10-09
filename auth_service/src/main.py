import asyncio
import logging

import fastapi
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from core.config import config
from events import event_producer
from routes.auth import auth_router
from routes.exceptions import apply_exception_handlers
from routes.middlewares import LimitUploadSize
from routes.users import user_router

app = fastapi.FastAPI(title='async arch')
logger = logging.getLogger('app-startup')
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
    # loop = asyncio.get_event_loop()
    # event_producer.set_loop(loop)
    # await event_producer.start()
    # logger.error('Kafka successfully connected')
    #
    # app.state.event_producer = event_producer
    pass


@app.on_event('shutdown')
async def shutdown():
    # await event_producer.stop()
    pass
