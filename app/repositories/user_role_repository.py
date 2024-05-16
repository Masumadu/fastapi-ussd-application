from app.core.repository import SQLBaseRepository
from app.models import UserModel


class UserRepository(SQLBaseRepository):
    model = UserModel
