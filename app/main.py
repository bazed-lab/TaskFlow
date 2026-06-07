from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.config import get_settings
from api.v1.router import api_router
from db.session import init_db


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
