import pinject
from fastapi import APIRouter, Request

from app.controllers import (
    AccountController,
    CustomerCareController,
    DepositController,
    OrderController,
    RegistrationController,
    UssdController,
)
from app.models import UserModel
from app.repositories import UserRepository
from app.services import RedisService

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        UssdController,
        RegistrationController,
        DepositController,
        UserRepository,
        RedisService,
        OrderController,
        AccountController,
        CustomerCareController,
    ],
)
ussd_controller: UssdController = obj_graph.provide(UssdController)

ussd_router = APIRouter()
ussd_base_url = "/ussd"


@ussd_router.post("/callback")
async def callback(request: Request):
    """Handles post call back from AT"""
    session_id = request.state.session_id
    user = UserModel.query_by_phone(phone=request.state.phone)
    return ussd_controller.start(session_id=session_id, user=user)
