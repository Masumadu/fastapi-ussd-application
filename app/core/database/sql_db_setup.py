from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.exceptions import AppException
from config import settings

# reminder: for establishing a connection to postgres
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=20,
    max_overflow=10,
    connect_args={"sslmode": "require" if settings.db_ssl else "prefer"},
    pool_pre_ping=True,
)

# reminder: for communicating or talking to postgres
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    except (DBAPIError, IntegrityError) as exc:
        db.rollback()
        raise AppException.BadRequestException(
            error_message=f"DatabaseError({exc.orig.args[0]})",
            context=f"DatabaseError({exc})",
        )
    finally:
        db.close()
