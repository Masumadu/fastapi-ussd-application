from app.models import UserModel
from app.repositories import UserRepository
from app.services import RedisService

from .base_menu_controller import BaseMenu


class OrderController(BaseMenu):
    """Serves order callbacks"""

    def __init__(
        self,
        user_repository: UserRepository,
        redis_service: RedisService,
    ):
        self.user_repository = user_repository
        self.redis_service = redis_service
        super().__init__(redis_service)

    def start(self, session_id: str):
        session = self.get_session(session_id=session_id)
        self.init_flow(session=session, handler="_home")
        return self.execute(session_id)

    def _home(self, session: dict):
        self.stack_prompt(session_id=session.get("session_id"), prompt="main_menu")
        self.set_handler(session_id=session.get("session_id"), method="_home_option")
        menu_text = """
        Select an option:

        1. Track Status
        2. Cancel
        0. Back
        """
        return self.ussd_proceed(menu_text=menu_text)

    def _home_option(self, session: dict):
        selected_option = session.get("current_input")
        session_id = session.get("session_id")
        if selected_option == "1":
            return self._track_status(session=session)
        elif selected_option == "2":
            return self._cancel(session=session)
        elif selected_option == "0":
            self.set_handler(session_id=session_id, method="_home")
            user = UserModel.query_by_phone(phone=session.get("phone"))
            return self.ussd_back(session_id, session=session, user=user)
        return self.ussd_end(session_id=session_id, menu_text="invalid input")

    def _track_status(self, session: dict):
        session_id = session.get("session_id")
        order = False
        self.stack_prompt(session_id=session_id, prompt="_home")
        self.set_handler(session_id=session_id, method="_track_status_option")
        if order:
            menu_text = """
            Your your order has been placed successfully

            Booking ID:123456
            Order Status:Submitted
            Pin :#4044848
            Expected delivery time: 24 hours

            Thank you for your order
            """
            return self.ussd_end(session_id=session_id, menu_text=menu_text)
        menu_text = """
        You don't have any pending order

        0. Back
        """
        return self.ussd_proceed(menu_text=menu_text)

    def _track_status_option(self, session: dict):
        selected_option = session.get("current_input")
        session_id = session.get("session_id")
        if selected_option == "0":
            return self.ussd_back(session_id=session_id, session=session)
        else:
            return self.ussd_end(session_id=session_id, menu_text="wrong input")

    def _cancel(self, session: dict):
        session_id = session.get("session_id")
        self.stack_prompt(session_id=session_id, prompt="_home")
        self.set_handler(session_id=session_id, method="_cancel_option")
        menu_text = """
        Please confirm to cancel order

        1. Confirm
        0. Back
        """
        return self.ussd_proceed(menu_text=menu_text)

    def _cancel_option(self, session: dict):
        selected_option = session.get("current_input")
        session_id = session.get("session_id")
        if selected_option == "1":
            return self._cancel_confirmation(session=session)
        elif selected_option == "0":
            return self.ussd_back(session_id=session_id, session=session)
        else:
            return self.ussd_end(session_id=session_id, menu_text="wrong input")

    def _cancel_confirmation(self, session):
        session_id = session.get("session_id")
        menu_text = """
        Your order cancelled successfully

        Your refund for the cancelled order has been
        credited back to your Newgas account for
        future use
        """
        return self.ussd_end(session_id=session_id, menu_text=menu_text)
