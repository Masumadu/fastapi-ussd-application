from app.models import UserModel
from app.repositories import UserRepository
from app.services import RedisService

from .base_menu_controller import BaseMenu


class DepositController(BaseMenu):
    """Serves deposit callbacks"""

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
        Select your preferred deposit:

        1. Cash Deposit
        0. Back
        """
        return self.ussd_proceed(menu_text=menu_text)

    def _home_option(self, session: dict):
        selected_option = session.get("current_input")
        session_id = session.get("session_id")
        if selected_option == "1":
            return self._cash_deposit(session=session)
        elif selected_option == "0":
            self.set_handler(session_id=session_id, method="_home")
            user = UserModel.query_by_phone(phone=session.get("phone"))
            return self.ussd_back(session_id, session=session, user=user)
        return self.ussd_end(session_id=session_id, menu_text="invalid input")

    def _cash_deposit(self, session: dict):
        session_id = session.get("session_id")
        self.stack_prompt(session_id=session_id, prompt="_home")
        self.set_handler(session_id=session_id, method="_cash_deposit_option")
        menu_text = """
        Cash deposit is the monetary value paid for the
        cylinder. Select your preferred cylinder size.

        1. 3kg steel
        2. 6kg steel
        3. 12kg steel
        4. 6kg composite
        5. 12kg composite
        0. Back
        """
        return self.ussd_proceed(menu_text=menu_text)

    def _cash_deposit_option(self, session: dict):
        selected_option = session.get("current_input")
        session_id = session.get("session_id")
        cylinders = {
            "1": "3kg steel",
            "2": "6kg steel",
            "3": "12kg steel",
            "4": "6kg composite",
            "5": "12kg composite",
        }
        if selected_option in cylinders:
            value = cylinders.get(selected_option)
            return self._deposit_confirmation(session=session, value=value)
        elif selected_option == "0":
            return self.ussd_back(session_id=session_id, session=session)
        else:
            return self.ussd_end(session_id=session_id, menu_text="wrong input")

    def _deposit_confirmation(self, session, value):
        session_id = session.get("session_id")
        self.stack_prompt(session_id=session_id, prompt="_cash_deposit")
        self.set_handler(session_id=session_id, method="_deposit_confirmation_option")
        menu_text = f"""
        Deposit Cost Steel {value}: GHS 100
        Gas Cost: GHS 70
        Total Cost: GHS 170

        1. Confirm Order
        0. Back
        """
        return self.ussd_proceed(menu_text=menu_text)

    def _deposit_confirmation_option(self, session: dict):
        selected_option = session.get("current_input")
        session_id = session.get("session_id")
        if selected_option == "1":
            return self._payment_gateway(session)
        elif selected_option == "0":
            return self.ussd_back(session_id=session_id, session=session)
        else:
            return self.ussd_end("unknown input", session_id)

    def _payment_gateway(self, session: dict):
        session_id = session.get("session_id")
        self.stack_prompt(session_id=session_id, prompt="_deposit_confirmation")
        self.set_handler(session_id=session_id, method="_payment_gateway_option")
        menu_text = """
        Please choose payment option

        1. MTN
        2. Vodafone
        3. AirtelTigo
        4. Pay on Delivery
        0. Back
        """
        return self.ussd_proceed(menu_text=menu_text)

    def _payment_gateway_option(self, session: dict):
        selected_option = session.get("current_input")
        session_id = session.get("session_id")
        if selected_option == "1":
            return self._mtn(session_id)
        elif selected_option == "2":
            return self._telecel(session_id)
        elif selected_option == "3":
            return self._airtel_tigo(session_id)
        elif selected_option == "4":
            return self._pay_on_delivery(session_id)
        elif selected_option == "0":
            return self.ussd_back(
                session_id=session_id, session=session, value="backoption"
            )
        else:
            return self.ussd_end(menu_text="invalid input", session_id=session_id)

    def _mtn(self, session_id):
        menu_text = """
        Thank you for your order!

        Dial *170#, select 6 then option 3 (My Approval)
        to complete payment
        """
        return self.ussd_end(session_id=session_id, menu_text=menu_text)

    def _telecel(self, session_id):
        menu_text = """
        Thank you for your order!

        Dial *110#, select 6 then option 5 (Approvals)
        to complete payment
        """
        return self.ussd_end(session_id=session_id, menu_text=menu_text)

    def _airtel_tigo(self, session_id):
        menu_text = """
        Thank you for your order!

        Dial *110#, select 6 then option 9 (Approvals)
        to complete payment
        """
        return self.ussd_end(session_id=session_id, menu_text=menu_text)

    def _pay_on_delivery(self, session_id):
        menu_text = """
        Your your order has been placed successfully

        Booking ID:123456
        Order Status:Submitted
        Pin :#4044848
        Expected delivery time: 24 hours

        Thank you for your order
        """
        return self.ussd_end(session_id=session_id, menu_text=menu_text)
