import json

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.services import RedisService


class UssdSessionMiddleware(BaseHTTPMiddleware, RedisService):
    async def dispatch(self, request: Request, call_next):
        form = await request.form()
        session_id = form.get("sessionId", "")
        phone_number = form.get("phoneNumber")
        text = form.get("text")
        text_array = text.split("*") if text else [""]
        user_input = text_array[-1]
        session = self.get(session_id)
        if not session:
            session = {
                "phone": phone_number,
                "session_id": session_id,
                "previous_inputs": text_array,
                "current_input": user_input,
            }
            self.set(session_id, json.dumps(session))
        else:
            session = json.loads(session)
            session["previous_inputs"] = text_array
            session["current_input"] = user_input
            self.set(session_id, json.dumps(session))
        request.state.session_id = session_id
        request.state.phone = phone_number
        response = await call_next(request)
        return response
