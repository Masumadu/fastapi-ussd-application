import redis
from fastapi.logger import logger
from redis.exceptions import RedisError

from app.core.exceptions import exception_message
from app.core.service_interfaces import CacheServiceInterface
from config import settings

REDIS_SERVER = settings.redis_server
REDIS_PASSWORD = settings.redis_password
REDIS_PORT = settings.redis_port

redis_conn = redis.Redis(
    host=REDIS_SERVER,
    port=REDIS_PORT,
    db=0,
    password=REDIS_PASSWORD,
    decode_responses=True,
)


class RedisService(CacheServiceInterface):
    def set(self, name: str, value: str, ex: int = None):
        try:
            redis_conn.set(name=name, value=value, ex=ex)
            return True
        except RedisError as exc:
            logger.critical(msg=exception_message(error="RedisError", message=str(exc)))
            return False

    def get(self, name: str):
        try:
            data = redis_conn.get(name)
            return data if data else None
        except RedisError as exc:
            logger.critical(msg=exception_message(error="RedisError", message=str(exc)))
            return False

    def delete(self, name: str):
        try:
            redis_conn.delete(name)
            return True
        except RedisError as exc:
            logger.critical(msg=exception_message(error="RedisError", message=str(exc)))
        return False
