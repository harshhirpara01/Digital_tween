"""
Main module of exchange backend.
"""
import logging
import os
import pathlib

from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette import status
from app.users.route import user
from app.behavior_logs.route import behavior_log
from app.model_train.route import model_train
from app.web.pages import web
from common.responses import errorResponse
from common.customized_log import CustomizeLogger
from middleware.request_auth_middleware import APIKeyValidatorMiddleware


"""
code for save logs in customise path
"""
logger = logging.getLogger(__name__)
module_path = str(pathlib.Path(__file__).parent.absolute())
config_path = str(os.path.join(module_path, "config", "logging_config.json"))

print("module_path --> ", module_path)
print("config_path --> ", config_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from shared.db import init_db

    init_db()
    yield


def create_app():
    debug = os.getenv("DEBUG", "true").lower() == "true"
    print("debug --> ", debug)

    app = FastAPI(
        title="digi tween | Project",
        docs_url="/docs" if debug else None,
        redoc_url="/redoc" if debug else None,
        openapi_url="/openapi.json" if debug else None,
        lifespan=lifespan,
    )

    origins = ["*"]

    # Add Custom API key validation middleware
    # app.add_middleware(APIKeyValidatorMiddleware, mdb=mdb)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_headers=["*"],
        allow_methods=["*"]
    )

    logger = CustomizeLogger.make_logger(config_path)
    app.logger = logger

    static_dir = os.path.join(module_path, "static")
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    app.include_router(web, tags=["WEB"])
    app.include_router(user,tags=["USERS"])
    app.include_router(behavior_log,tags=["BEHAVIOR_LOGS"])
    app.include_router(model_train,tags=['Model_Train'])

    return app


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     abcd = exc.errors()
#     error_msgs = ", ".join([f"'{i['loc'][1]}': {i['msg']}" for i in abcd])
#
#     logger.error(error_msgs)
#     return errorResponse(status.HTTP_422_UNPROCESSABLE_ENTITY, error_msgs)


app = create_app()
if __name__ == "__main__":
    uvicorn.run(app)