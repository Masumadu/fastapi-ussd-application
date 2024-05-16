from app.models import UserModel
from app.repositories import UserRepository
from app.services import RedisService

from .base_menu_controller import BaseMenu


class AccountController(BaseMenu):
    """Serves account callbacks"""

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
        Account Balance

        Deposit Cost: GHS 500
        Gas Cost: GHS 100

        0. Back
        """
        return self.ussd_proceed(menu_text=menu_text)

    def _home_option(self, session: dict):
        selected_option = session.get("current_input")
        session_id = session.get("session_id")
        if selected_option == "0":
            self.set_handler(session_id=session_id, method="_home")
            user = UserModel.query_by_phone(phone=session.get("phone"))
            return self.ussd_back(session_id, session=session, user=user)
        return self.ussd_end(session_id=session_id, menu_text="invalid input")
