# Standard Library Imports
import os

# Third party imports
import pytest

# Application level imports
from environment import Environment
from config_reader import ConfigReader
from _logger import logger


class Person():
    def __init__(self, name: str, age: int):
        self.name: str = name
        self.age: int = age

    def get_name(self) -> str:
        return self.name

    def get_age(self) -> int:
        return self.age
    
    @staticmethod
    def parse_person(person_string: str):
        if not isinstance(person_string, str):
            msg = f"Attempted to parse a non string object: {person_string}"
            logger.error(msg)
            raise TypeError(msg)
        if person_string.count(':') != 1:
            msg = "a 'person string' must have exactly one ':' character, separating the name and age"
            logger.error(msg)
            raise ValueError(msg)
        
        parse = person_string.split(':')

        if not parse[1].isdigit():
            msg = f"The string after the ':' character in a person string must be an integer.  Instead, {parse[1]} was passed."
            logger.error(msg)
            raise ValueError(msg)
        
        return Person(parse[0], int(parse[1]))




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

def test_read_field_local():
    environment = Environment()
    reader = ConfigReader(environment)

    assert reader.read_field("test.test1", str, "fail") == "local1"
    assert reader.read_field("test.test2", str, "fail") == "local2"
    assert reader.read_field("test.default", str, "fail") == "constant"
    assert reader.read_field("test.test3", str, "fail") == "fail"

def test_read_field_dev():
    os.environ[Environment._app_environment_key] = "dev"
    environment = Environment()
    reader = ConfigReader(environment)

    assert reader.read_field("test.test1", str, "fail") == "dev1"
    assert reader.read_field("test.test2", str, "fail") == "dev2"
    assert reader.read_field("test.default", str, "fail") == "constant"
    assert reader.read_field("test.test3", str, "fail") == "fail"

def test_read_field_qa():
    os.environ[Environment._app_environment_key] = "qa"
    environment = Environment()
    reader = ConfigReader(environment)

    assert reader.read_field("test.test1", str, "fail") == "qa1"
    assert reader.read_field("test.test2", str, "fail") == "qa2"
    assert reader.read_field("test.default", str, "fail") == "constant"
    assert reader.read_field("test.test3", str, "fail") == "fail"

def test_read_field_prod():
    os.environ[Environment._app_environment_key] = "prod"
    environment = Environment()
    reader = ConfigReader(environment)

    assert reader.read_field("test.test1", str, "fail") == "prod1"
    assert reader.read_field("test.test2", str, "fail") == "prod2"
    assert reader.read_field("test.default", str, "fail") == "constant"
    assert reader.read_field("test.test3", str, "fail") == "fail"

def test_read_field_no_handler():
    reader = ConfigReader(Environment())

    with pytest.raises(TypeError) as e:
        reader.read_field("bad", dict, {"this does not": "Work"})

    assert "ERROR: No handler exists" in str(e)

def test_non_existant_section():
    os.environ[Environment._app_environment_key] = "none"
    environment = Environment()
    reader = ConfigReader(environment)

    assert reader.read_field("test.test1", str, "fail") == "fail"
    assert reader.read_field("test.test2", str, "fail") == "fail"
    assert reader.read_field("test.default", str, "fail") == "constant"
    assert reader.read_field("test.test3", str, "fail") == "fail"

def test_non_existant_file():
    os.environ[Environment._config_location_key] = "None"
    environment = Environment()
    reader = ConfigReader(environment)

    assert reader._app_environment == "DEFAULT"
    assert reader.read_field("test.test1", str, "fail") == "fail"
    assert reader.read_field("test.test2", str, "fail") == "fail"
    assert reader.read_field("test.default", str, "fail") == "fail"
    assert reader.read_field("test.test3", str, "fail") == "fail"

def test_add_handler():
    reader = ConfigReader(Environment())

    reader.add_handler(Person, Person.parse_person)

    guts = reader.read_field("test.guts", Person, Person("None", -1))
    casca = reader.read_field("test.casca", Person, Person("None", -1))

    assert guts.get_name() == "guts"
    assert guts.get_age() == 24

    assert casca.get_name() == "casca"
    assert casca.get_age() == 24

def test_add_handler_no_type():
    reader = ConfigReader(Environment())

    with pytest.raises(TypeError) as e:
        reader.add_handler("Person", Person.parse_person)

    assert "Instead, a <class 'str'> was passed." in str(e)

def test_add_handler_existing_type():
    reader = ConfigReader(Environment())

    reader.add_handler(Person, Person.parse_person)
    with pytest.raises(ValueError) as e:
        reader.add_handler(Person, Person.parse_person)

    assert "A handler for type <class 'test.test_config_reader.Person'> already exists inside of the ConfigReader." in str(e)

def test_add_handler_not_callable():
    reader = ConfigReader(Environment())

    with pytest.raises(TypeError) as e:
       reader.add_handler(Person, "Not Callable")

    assert "the handler parameter must be a Callable" in str(e)

def test_callable_exception():
    reader = ConfigReader(Environment())
    reader.add_handler(Person, Person.parse_person)

    person = reader.read_field("test.bad", Person, Person("Failure", -1))
    assert person.get_name() == "Failure"
    assert person.get_age() == -1