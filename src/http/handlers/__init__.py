from fastapi import FastAPI

from .health_check import router as hc_router
from .news import router as news_router


def setup_handlers(app: FastAPI):
    app.include_router(hc_router)
    app.include_router(news_router)
