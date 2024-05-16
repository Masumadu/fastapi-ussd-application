import os

from app import constants, create_app

config_env = os.getenv("APP_CONFIG")
assert config_env != constants.TESTING_ENVIRONMENT, constants.ENV_ERROR.format(
    config_env
)
app = create_app()
