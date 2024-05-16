import json

from fastapi import Response

from app.services import RedisService


class BaseMenu:
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        self.default = "main_menu"

    def main_menu(self, session: dict, user: str):
        """serves the home menu"""
        self.set_handler(session_id=session.get("session_id"), method=self.default)
        menu_text = f"Hello {user}, welcome to NewGas,\n Choose a service\n"
        menu_text += " 1. Make Deposit\n"
        menu_text += " 2. Order Status\n"
        menu_text += " 3. Account Balance\n"
        menu_text += " 4. Contact Customer Care\n"
        return self.ussd_proceed(menu_text)

    def init_flow(self, session: dict, handler=None):
        if not session.get("handler") or session.get("handler") == self.default:
            self.update_session(
                session_id=session.get("session_id"),
                obj_in={
                    "current_input": None,
                    "handler": handler,
                    "service_prompts": [],
                },
            )
        return None

    def ussd_proceed(self, menu_text):
        """proceeds to the next prompt"""
        menu_text = f"CON {menu_text}"
        response = Response(menu_text, 200)
        response.headers["Content-Type"] = "text/plain"
        return response

    def ussd_end(self, menu_text, session_id):
        """ends the ussd flow"""
        self.redis_service.delete(session_id)
        menu_text = f"END {menu_text}"
        response = Response(menu_text, 200)
        response.headers["Content-Type"] = "text/plain"
        return response

    def ussd_back(self, session_id: str, **kwargs):
        """returns the previous prompt"""
        prompt = self.pop_prompt(session_id=session_id)
        if kwargs:
            return getattr(self, prompt)(**kwargs)
        return getattr(self, prompt)()

    def start(self, **kwargs):
        """start the ussd flow"""
        raise NotImplementedError

    def execute(self, session_id: str, **kwargs):
        """returns the next prompt"""
        session = self.get_session(session_id)
        return getattr(self, session.get("handler"))(session=session)

    def get_session(self, session_id: str):
        """returns the user session"""
        return json.loads(self.redis_service.get(session_id))

    def set_handler(self, session_id: str, method: str):
        """set the handler to process the prompt"""
        return self.update_session(session_id=session_id, obj_in={"handler": method})

    def update_session(self, session_id: str, obj_in: dict):
        """update the user session parameters"""
        session = self.get_session(session_id)
        for field in obj_in:
            session[field] = obj_in.get(field)
        self.redis_service.set(session_id, json.dumps(session))
        return session

    def stack_prompt(self, session_id: str, prompt: str):
        """add current prompt"""
        session = self.get_session(session_id)
        service_prompts = session.get("service_prompts")
        if prompt not in service_prompts:
            service_prompts.append(prompt)
        self.redis_service.set(session_id, json.dumps(session))
        return session

    def pop_prompt(self, session_id: str):
        """show the immediate prompt"""
        session = self.get_session(session_id)
        service_prompts = session.get("service_prompts")
        prompt = service_prompts.pop(-1)
        self.redis_service.set(session_id, json.dumps(session))
        return prompt
