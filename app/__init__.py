from logging.config import dictConfig

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi_pagination import add_pagination
from sqlalchemy.exc import DBAPIError
from starlette.middleware.cors import CORSMiddleware

from app import api
from app.core.exceptions import (
    AppException,
    AppExceptionCase,
    app_exception_handler,
)
from app.core.log import log_config
from app.utils import UssdSessionMiddleware
from config import settings

dictConfig(log_config())


def create_app():
    app = FastAPI(
        title="Nova Authentication Server",
        description="provides backend for ussd application",  # noqa
        version="1.0.0",
        docs_url="/ussd/docs",
        swagger_ui_oauth2_redirect_url="/ussd/docs/oauth2-redirect",
        openapi_url="/ussd/openapi.json",
    )
    register_middlewares(app)
    register_api_routers(app)
    register_extensions(app)
    return app


def register_api_routers(app: FastAPI):
    api.init_api_v1(app)

    @app.get("/newgas/", include_in_schema=False)
    def index():
        return RedirectResponse("/docs")

    return None


def register_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split("|"),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(UssdSessionMiddleware)

    return None


def register_extensions(app: FastAPI):
    """Register extensions."""
    add_pagination(app)

    @app.exception_handler(HTTPException)
    def handle_http_exception(request, exc):
        return app_exception_handler.http_exception_handler(exc)

    @app.exception_handler(DBAPIError)
    def handle_db_exception(request, exc):
        return app_exception_handler.db_exception_handler(exc)

    @app.exception_handler(AppExceptionCase)
    def handle_app_exceptions(request, exc):
        return app_exception_handler.app_exception_handler(exc)

    @app.exception_handler(RequestValidationError)
    def handle_validation_exceptions(request, exc):
        return app_exception_handler.validation_exception_handler(exc)

    return None
