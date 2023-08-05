# Standard Library Imports
import os

# Third party imports
import pytest

# Application level imports
from environment import Environment
from config_reader import ConfigReader
from _logger import logger
from config_object import Config
from namespace import NameSpace


@pytest.fixture(autouse=True)
def reset_env():
    set_env()
    yield
    clear_env()

def set_env():
    os.environ[Environment._app_environment_key] = "local"
    os.environ[Environment._config_location_key] = "test/resources/properties_config.ini"

def clear_env():
    if Environment._log_level_key in os.environ:
        del os.environ[Environment._log_level_key]
    if Environment._app_environment_key in os.environ:
        del os.environ[Environment._app_environment_key]
    if Environment._config_location_key in os.environ:
        del os.environ[Environment._config_location_key]

def test_end_to_end():
    config = Config()

    fields = NameSpace("test")
    fields.add_entry("test1", str, "fail")
    fields.add_entry("test2", str, "fail")
    fields.add_entry("default", str, "fail")

    config.add_namespace(fields)

    assert config["test"]["test1"] == "local1"
    assert config["test"]["test2"] == "local2"
    assert config["test"]["default"] == "constant"

    fields = NameSpace("pytest")
    fields.add_entry("test1", str, "fail")
    fields.add_entry("test2", str, "fail")

    config.add_namespace(fields)

    assert config["pytest"]["test1"] == "local3"
    assert config["pytest"]["test2"] == "local4"

def test_duplicate_namespace():
    config = Config()

    fields = NameSpace("test")
    fields.add_entry("test1", str, "fail")
    fields.add_entry("test2", str, "fail")
    fields.add_entry("default", str, "fail")

    config.add_namespace(fields)

    assert config["test"]["test1"] == "local1"
    assert config["test"]["test2"] == "local2"
    assert config["test"]["default"] == "constant"

    fields = NameSpace("test")
    fields.add_entry("test1", str, "fail")
    fields.add_entry("test2", str, "fail")

    with pytest.raises(ValueError) as e:
        config.add_namespace(fields)

    assert "ERROR - namespace test already exists" in str(e)
    assert config["test"]["test1"] == "local1"
    assert config["test"]["test2"] == "local2"