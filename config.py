import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from app import constants


class BaseConfig(BaseSettings):
    # reminder: general application settings
    app_config: str = constants.DEVELOPMENT_ENVIRONMENT
    app_name: str = constants.APPLICATION_NAME
    log_header: str = constants.LOG_HEADER
    cors_origins: str = "*"
    app_root: str = str(Path(__file__).parent)
    maintainer_mail_address: str = "michaelasumadu1@gmail.com"
    # reminder: postgres database config
    db_host: str = ""
    db_user: str = ""
    db_password: str = ""
    db_name: str = ""
    db_port: str = ""
    db_ssl: bool = True
    # reminder: redis server config
    redis_server: str = ""
    redis_port: str = ""
    redis_password: str = ""
    # MAIL CONFIGURATION
    mail_server: str = ""
    mail_server_port: str = ""
    default_mail_sender: str = ""
    default_mail_sender_address: str = ""
    default_mail_sender_password: str = ""

    @property
    def SQLALCHEMY_DATABASE_URI(self):  # noqa
        return "postgresql+psycopg2://{db_user}:{password}@{host}:{port}/{db_name}".format(  # noqa
            db_user=self.db_user,
            host=self.db_host,
            password=self.db_password,
            port=self.db_port,
            db_name=self.db_name,
        )

    class Config:
        env_file = ".env"
        extra = "allow"


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    test_db_host: str = ""
    test_db_user: str = ""
    test_db_password: str = ""
    test_db_name: str = ""
    test_db_port: str = ""
    db_ssl: bool = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):  # noqa
        return "postgresql+psycopg2://{db_user}:{password}@{host}:{port}/{db_name}".format(
            # noqa
            db_user=self.test_db_user,
            host=self.test_db_host,
            password=self.test_db_password,
            port=self.test_db_port,
            db_name=self.test_db_name,
        )


def get_settings():
    load_dotenv(".env")
    config_cls_dict = {
        constants.DEVELOPMENT_ENVIRONMENT: DevelopmentConfig,
        constants.PRODUCTION_ENVIRONMENT: ProductionConfig,
        constants.TESTING_ENVIRONMENT: TestingConfig,
    }
    config_name = os.getenv("APP_CONFIG")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
