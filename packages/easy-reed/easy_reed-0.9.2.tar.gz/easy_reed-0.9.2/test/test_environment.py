# Standard Library Imports
import os

# Third party imports
import pytest

# Application level imports
from environment import Environment


@pytest.fixture(autouse=True)
def reset_env():
    clear_env()
    yield
    clear_env()

def clear_env():
    if Environment._log_level_key in os.environ:
        del os.environ[Environment._log_level_key]
    if Environment._app_environment_key in os.environ:
        del os.environ[Environment._app_environment_key]
    if Environment._config_location_key in os.environ:
        del os.environ[Environment._config_location_key]

def test_default_setup():
    environment = Environment()
    assert environment._log_level == Environment._log_level_default
    assert environment._app_environment == Environment._app_environment_default
    assert environment._app_config_location == Environment._app_config_location_default

def test_log_level():
    os.environ[Environment._log_level_key] = "test"
    environment = Environment()
    assert environment._log_level == "test"
    assert environment._app_environment == Environment._app_environment_default
    assert environment._app_config_location == Environment._app_config_location_default

def test_app_env():
    os.environ[Environment._app_environment_key] = "test"
    environment = Environment()
    assert environment._log_level == Environment._log_level_default
    assert environment._app_environment == "test"
    assert environment._app_config_location == Environment._app_config_location_default

def test_config_location():
    os.environ[Environment._config_location_key] = "test"
    environment = Environment()
    assert environment._log_level == Environment._log_level_default
    assert environment._app_environment == Environment._app_environment_default
    assert environment._app_config_location == "test"

def test_log_level_AND_app_env():
    os.environ[Environment._log_level_key] = "test1"
    os.environ[Environment._app_environment_key] = "test2"
    environment = Environment()
    assert environment._log_level == "test1"
    assert environment._app_environment == "test2"
    assert environment._app_config_location == Environment._app_config_location_default

def test_log_level_AND_config_location():
    os.environ[Environment._log_level_key] = "test1"
    os.environ[Environment._config_location_key] = "test2"
    environment = Environment()
    assert environment._log_level == "test1"
    assert environment._app_environment == Environment._app_environment_default
    assert environment._app_config_location == "test2"

def test_app_env_AND_config_location():
    os.environ[Environment._app_environment_key] = "test1"
    os.environ[Environment._config_location_key] = "test2"
    environment = Environment()
    assert environment._log_level == Environment._log_level_default
    assert environment._app_environment == "test1"
    assert environment._app_config_location == "test2"

def test_all():
    os.environ[Environment._log_level_key] = "test1"
    os.environ[Environment._app_environment_key] = "test2"
    os.environ[Environment._config_location_key] = "test3"
    environment = Environment()
    assert environment._log_level == "test1"
    assert environment._app_environment == "test2"
    assert environment._app_config_location == "test3"