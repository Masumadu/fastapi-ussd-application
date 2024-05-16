from fastapi import FastAPI

from .endpoints import ussd_base_url, ussd_router


def init_api_v1(app: FastAPI):
    app.include_router(router=ussd_router, tags=["Ussd"], prefix=ussd_base_url)
