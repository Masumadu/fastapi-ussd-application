from app.services import RedisService

from .account_controller import AccountController
from .base_menu_controller import BaseMenu
from .customer_care_controller import CustomerCareController
from .deposit_controller import DepositController
from .order_controller import OrderController
from .registeration_controller import RegistrationController


class UssdController(BaseMenu):
    def __init__(
        self,
        redis_service: RedisService,
        registration_controller: RegistrationController,
        deposit_controller: DepositController,
        order_controller: OrderController,
        account_controller: AccountController,
        customer_care_controller: CustomerCareController,
    ):
        self.registration_controller = registration_controller
        self.redis_service = redis_service
        self.deposit_controller = deposit_controller
        self.order_controller = order_controller
        self.account_controller = account_controller
        self.customer_care_controller = customer_care_controller
        super().__init__(redis_service)

    def start(self, session_id, user):
        if not user:
            return self.registration_controller.start(session_id=session_id)
        elif user and not user.is_verified:
            return self.registration_controller.start(
                session_id=session_id, handler="_review"
            )
        return self.execute(session_id, user.first_name)

    def main_menu_option(self, session_id: str, option: str):
        menus = {
            "1": self.deposit_controller.start,
            "2": self.order_controller.start,
            "3": self.account_controller.start,
            "4": self.customer_care_controller.start,
        }
        selected_menu = menus.get(option)
        if not selected_menu:
            return self.ussd_end(session_id=session_id, menu_text="invalid input")
        return selected_menu(session_id=session_id)  # noqa

    def execute(self, session_id: str, user: str = None):
        session = self.get_session(session_id=session_id)
        if not session.get("current_input"):
            return self.main_menu(session, user)
        if session.get("handler") == self.default:
            session["base_option"] = session.get("current_input")
            session = self.update_session(session_id=session_id, obj_in=session)
        return self.main_menu_option(session_id, session.get("base_option"))
