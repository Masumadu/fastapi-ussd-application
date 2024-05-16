import logging
import sys
from logging.config import dictConfig

from alembic import command
from alembic.config import Config
from sqlalchemy.exc import SQLAlchemyError

from app.core.log import log_config


def run_alembic_migration():
    alembic_cfg = Config("./alembic.ini")
    command.upgrade(alembic_cfg, "head")


def log_error(level: int, message: object, exec_info: bool = False):
    dictConfig(log_config())
    logger = logging.getLogger(__name__)
    logger.log(level, message, exc_info=exec_info)
    sys.exit(1)


try:
    run_alembic_migration()
except SQLAlchemyError:
    log_error(level=50, message=None, exec_info=True)
