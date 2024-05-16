import uuid

import sqlalchemy as sa

from app.core.database import Base, get_db_session
from app.utils import GUID


class UserModel(Base):
    __tablename__ = "users"
    id = sa.Column(GUID, primary_key=True, default=uuid.uuid4)
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    phone = sa.Column(sa.String, nullable=False, unique=True, index=True)
    _pin = sa.Column("pin", sa.String)
    address = sa.Column(sa.String)
    is_verified = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
    is_deleted = sa.Column(sa.Boolean, default=False)
    deleted_at = sa.Column(sa.DateTime(timezone=True))

    @classmethod
    def query_by_phone(cls, phone: str):
        with get_db_session() as db_session:
            result = db_session.query(cls).filter(cls.phone == phone).first()
        return result
