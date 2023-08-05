""" config_reader module - responsible for reading in config fields and keeping track of type handlers

the core of this module is the ConfigReader object.  Using an environment.Environment object, this class is able
to find the config file location and read it in.  When a request to read a config field is made to the ConfigReader,
the expected object type and a fallback will be given.  The ConfigReader will search for the given field in the section
for the given app environment, specified in the environment.Environment object.  If found, it will attempt to parse it into
the requested type using a registered type handler for that type.  Should any problem occur, an error is logged out and the
fallback default will be returned.  This object comes pre registered with a list parser.  It can parse a list of strings
from a config string.

MODULE CLASSES
--------------
ConfigReader - responsible for reading in config fields and keeping track of type handlers

MODULE FUNCTIONS
----------------
list_converter(element: str) -> list[str]
    - converts a string (element) into a list of strings if possible; otherwise, throws an exception

@Author - Reed Nathaniel Schick
@DateCreated - 4/26/2023
@DateModified - 4/26/2023
"""


# Standard Library Imports
from typing import Any, Dict, Tuple, Callable, List
from configparser import ConfigParser
import os

# Application Imports
from easy_reed._logger import logger
from easy_reed.namespace import NameSpace
from easy_reed.environment import Environment


def list_converter(element: str) -> List[str]:
    """ Function to convert a formatted string into a list; assumes all elements are strings

    this function takes a string of the format '[element1, element2, element3]' and converts it into
    a python list with the given string elements.  The string must begin with '[' and end with ']'.  Commas
    will be used as delimiters.

    Parameters
    ----------
    element: str
        - A string the represents a list to be parsed into a python list object

    Throws
    ------
    TypeError
        - if 'element' is not of type string
    ValueError
        - if 'element' does not begin with '[' and end with ']'

    Returns
    -------
    List[str]
        - the parsed Python list object
    """
    # Make sure the element to convert is a string
    if type(element) != str:
        msg = f"element for list conversion must be of type string.  Instead, a {type(element)} was passed."
        logger.error(msg)
        raise TypeError(msg)
    
    # Make sure the string is formatted correctly - starts with '[' and ends with ']'
    value = element.strip()
    if value[0] != "[" or value[-1] != "]":
        msg = f"The string representing the list must start with '[' and end with ']'.  Instead, {element} was passed."
        logger.error(msg)
        raise ValueError(msg)

    # split the string into a list by comma.  Strip any extra white space    
    my_list = value[1:-1].split(',')
    for index, value in enumerate(my_list):
        my_list[index] = value.strip()

    return my_list


class ConfigReader():
    """ Responsible for reading config fields into the easy_reed.config object via use of a ConfigParser

    The ConfigReader is responsible for fetching config fields and loading them into the easy_reed.config object.
    It is a helper class used by the config.Config object itself and the end user should not expect to interface with
    it directly.  Handlers can be added to the ConfigReader to enable automatic conversion from config strings to any
    desired type.  This class will utilize the Environment initialized by the config.Config object in order to determine
    how and where to read the config fields.

    Instance Variables
    ------------------
    _app_environment: str
        - the app environment, as read in by the environment.  This specifies which section of the config file to use when parsing
    _configparser: ConfigParser
        - the underlying ConfigParser object that is used to load config properties
    _converters: dict[type, Callable]
        - a dictionary that maps object types to the Callable function that can convert strings into said type
    _counter: int
        - an underlying variable used to avoid class name conflicts when adding new handlers to the ConfigReader

    Methods
    -------
    add_handler(self, typ: type, handler: Callable) -> Callable
        - Add a new handler function of type typ to the ConfigReader; enables automatic string to type conversion.
    read_field(self, field_name: str, typ: type, default: Any) -> Any
        - Read a field from the config file, and parse into into the given type.  return the default if a problem occurs.
    """
    
    def __init__(self, environment: Environment):
        # Set the app environment for easier access
        self._app_environment = environment.get_app_environment()

        # Create the config parser and add the list converter
        self._configparser = ConfigParser(
            strict=True,
            converters = {
                'list': list_converter
            }
        )

        # If the config file exists, read it in
        if not os.path.exists(environment.get_config_location()):
            logger.error(f"Config file {environment.get_config_location()} does not exist.  Config defaults will be used.")
        else:
            with open(environment.get_config_location()) as f:
                self._configparser.read_file(f)

        # If there isn't a section in the parser associated with the app environment, set it to DEFAULT
        if not self._app_environment in self._configparser:
            logger.error(f"App environment was read in as {self._app_environment}, but no section exists for it in the config file.  Setting _app_environment to 'DEFAULT'.")
            self._app_environment = "DEFAULT"

        # Initialize the converters map and counter
        self._converters = {
            list: self._configparser.getlist,
            int: self._configparser.getint,
            float: self._configparser.getfloat,
            bool: self._configparser.getboolean,
            str: self._configparser.get
        }
        self._counter = 0

    def read_field(self, field_name: str, typ: type, default: Any) -> Any:
        """ Read a field from the config file, and parse into into the given type.  return the default if a problem occurs.

        This function will attempt to read 'field_name' in from the config file.  If the field exists, then the function will
        attempt to parse it into type typ.  If any problem occurs during parsing, the default will be returned.

        Parameters
        ----------
        field_name: str
            - the field name to read from the config file
        typ: type
            - the type to convert the config field into
        default: Any
            - The default to return if a problem occurs
        
        Raises
        ------
        TypeError
            - When the wrong parameter types are passed to this function, or if the default value is not of the type
              specified by the typ parameter.  Also thrown if typ specifies a type with no handler.
        ValueError
            - When the field_name is an empty string, or the field_name already exists within this namespace.

        Returns
        -------
        Any
            - The config field that gets read in and converted into type typ
        """
        logger.debug(f"attempting to load config field {field_name} as type {typ}")
        # Validate the field entry
        NameSpace.validate_entry(field_name, typ, default)

        # Make sure a type converter exists
        if typ not in self._converters:
            msg = f"ERROR: No handler exists to convert strings into type {typ}."
            logger.error(msg)
            raise TypeError(msg)

        # Try to read in the field, using self._app_environment as the section, field_name as the field, and default as the fallback
        try:
            result = self._converters[typ](self._app_environment, field_name, fallback=default)
            logger.debug(f"successfully read in config field {field_name} as {result}.")
            return result
        
        # If a problem occurs, log it and return the default
        except Exception as e:
            logger.error(f"A problem occured while attempting to parse config field {field_name}.\n  Its type converter threw the following error: {str(e)}\nthe field will be defaulted to its given default: {default}")
            return default

    def add_handler(self, typ: type, handler: Callable) -> Callable:
        """ Adds a new type handler to the config_reader.
        
        If you want to be able to represent more types of objects in your config file as strings, you can
        define a converter for the given type and register it here.  For example, maybe you have a 'Person' object
        with an 'age' and a 'name'.  You could define the Person in a string such as 'Sam:37', and write a function
        that can parse the name and age from the string.  Then, the config field can be auto converted to the proper
        type and stored in the config dictionary.

        Parameters
        ----------
        typ: type
            - specifies the object type that the given handler will convert to
        handler: Callable
            - a function that converts a string into the type specified by typ

        Throws
        ------
        TypeError
            - if typ is not of type type, or if handler is not of type Callable
        ValueError
            - if there is already an existing handler for the given type

        Returns
        -------
        Callable
            - the method of the configparser that is created for parsing the given type
        """
        # Make sure that typ specifies a valid type
        if not isinstance(typ, type):
            msg = f"the typ parameter must specify the type that the handler Converts to.  Instead, a {type(typ)} was passed."
            logger.error(msg)
            raise TypeError(msg)

        # Make sure that there is not an existing handler for type typ
        if typ in self._converters.keys():
            msg = f"A handler for type {typ} already exists inside of the ConfigReader."
            logger.error(msg)
            raise ValueError(msg)
        
        # Make sure that handler is a Callable function
        if not isinstance(handler, Callable):
            msg = f"the handler parameter must be a Callable that converts a string to the given type typ.  Instead, a {type(handler)} was passed."
            logger.error(msg)
            raise TypeError(msg)

        # Add the handler - we use a UID, counter, to ensure that the name hasn't been used.  A secondary dictionary
        # called self._converters maps each type object to its given converter function
        self._configparser._converters[f'{self._counter}'] = handler
        self._converters[typ] = getattr(self._configparser, f"get{self._counter}")
        self._counter = self._counter + 1
        return self._converters[typ]
