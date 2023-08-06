import logging

from fastapi import FastAPI

from .endpoints.predict import router as predict_router
from .endpoints.train import router as train_router

logging.basicConfig(level=logging.INFO)


def create_app():
    app = FastAPI()
    app.include_router(train_router, tags=["train"])
    app.include_router(predict_router, tags=["predict"])
    return app
