import uvicorn

from core.config import config

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True, host=config.host, port=config.port, log_level='info')
