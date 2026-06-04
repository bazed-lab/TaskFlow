import uvicorn
from fastapi import FastAPI

from core.config import get_settings
from api.v1.router import api_router

settings = get_settings()

app = FastAPI()
app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)