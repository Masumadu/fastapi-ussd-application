from app.repositories import UserRepository
from app.services import RedisService

from .base_menu_controller import BaseMenu


class CustomerCareController(BaseMenu):
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
        menu_text = """
        Thank you for contacting customer care

        Kindly reach us on any of the numbers
        0200000000/0500000000
        """
        return self.ussd_end(session_id=session.get("session_id"), menu_text=menu_text)
