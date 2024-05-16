from app.repositories import UserRepository
from app.services import RedisService

from .base_menu_controller import BaseMenu


class RegistrationController(BaseMenu):
    """Serves registration callbacks"""

    def __init__(
        self,
        user_repository: UserRepository,
        redis_service: RedisService,
    ):
        self.user_repository = user_repository
        self.redis_service = redis_service
        super().__init__(redis_service)

    def start(self, session_id: str, handler=None):
        session = self.get_session(session_id=session_id)
        self.init_flow(session=session, handler=handler or "_home")
        return self.execute(session_id)

    def _home(self, session: dict):
        self.set_handler(method="_home_option", session_id=session.get("session_id"))
        menu_text = """
        Welcome to Newgas
        Simple follow the prompts to get started

        1. Registration

        """
        return self.ussd_proceed(menu_text=menu_text)

    def _home_option(self, session: dict):
        selected_option = session.get("current_input")
        session_id = session.get("session_id")
        if selected_option == "1":
            return self._get_name(session=session)
        return self.ussd_end(session_id=session_id, menu_text="invalid input")

    def _get_name(self, session: dict):
        self.set_handler(
            session_id=session.get("session_id"), method="_get_name_option"
        )
        return self.ussd_proceed(menu_text="Enter Name:")

    def _get_name_option(self, session: dict):
        user_input = session.get("current_input")
        session_id = session.get("session_id")
        if user_input:
            return self._get_address(session=session)
        return self.ussd_end(session_id=session_id, menu_text="name required")

    def _get_address(self, session: dict):
        self.set_handler(
            session_id=session.get("session_id"), method="_get_address_option"
        )
        menu_text = "Enter your digital address/location:"
        return self.ussd_proceed(menu_text=menu_text)

    def _get_address_option(self, session: dict):
        user_input = session.get("current_input")
        session_id = session.get("session_id")
        if user_input:
            return self._register_user(session=session)
        return self.ussd_end(session_id=session_id, menu_text="name required")

    def _register_user(self, session: dict):
        previous_inputs = session.get("previous_inputs")
        address = session.get("current_input")
        name = previous_inputs[-2].split(" ")
        last_name = name[1] if len(name) > 1 else None
        self.user_repository.create(
            obj_in={
                "first_name": name[0],
                "last_name": last_name,
                "phone": session.get("phone"),
                "address": address,
            }
        )
        menu_text = """
        Registration is initiated!

        Onboarding is under process.
        Our customer care will reach out to you to finalize the process
        Thank You.
        """
        return self.ussd_end(session_id=session.get("session_id"), menu_text=menu_text)

    def _review(self, session: dict):
        menu_text = """
        Your onboarding is currently under process and
        our onboarding Agent will contact you shortly.
        Kindly contact customer service (020040090) if
        you don't receive a response within next 24 hours.
        """
        return self.ussd_end(session_id=session.get("session_id"), menu_text=menu_text)
