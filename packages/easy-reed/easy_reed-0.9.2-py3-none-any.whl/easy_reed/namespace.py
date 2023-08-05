""" namespace module - responsible for defining config namespaces to add to the config object

At its core, easy_reed attempts to make it simple to configure multiple dependencies from a single object, the
easy_reed.config.Config object.  When a library wishes to register its configuration fields with the Config
object, it will do so be defining a namespace.  A namespace is initiated with a name; this will be the name
used to access the config fields (e.g. config[name][field1], config[name][field2], etc).  Once a namespace has been
initiated, config fields can be defined through the NameSpace.add_entry method.  Once a namespace has been defined,
it can be registered to the config dictionary via the Config.add_namespace method.

MODULE CLASSES
--------------
NameSpace - used to define config fields for a module

@Author - Reed Nathaniel Schick
@DateCreated - 4/26/2023
@DateModified - 4/28/2023
"""

# Standard Library Imports
from typing import  Any, Dict, Callable, Tuple
from configparser import ConfigParser

# Application level imports
from easy_reed._logger import logger

class NameSpace():
    """ Used to define config fields for a module

    At its core, easy_reed attempts to make it simple to configure multiple dependencies from a single object, the
    easy_reed.config.Config object.  When a library wishes to register its configuration fields with the Config
    object, it will do so be defining a namespace.  A namespace is initiated with a name; this will be the name
    used to access the config fields (e.g. config[name][field1], config[name][field2], etc).  Once a namespace has been
    initiated, config fields can be defined through the NameSpace.add_entry method.  Once a namespace has been defined,
    it can be registered to the config dictionary via the Config.add_namespace method.

    INSTANCE VARIABLES
    ------------------
    name: str
        - defines the name of the namespace, used when accessing its config fields
    entries: list
        - a list of config field entries added to this namespace

    METHODS
    -------
    get_name(self) -> str
        - simple getter method for the name of the namespace
    add_entry(self, field_name: str, typ: type, default: Any) -> Tuple[str, type, Any]
        - add a new config field to this namespace
    has_field(self, field_name: str) -> bool
        - check to see if a config field with the given name exists in this NameSpace
    """

    def __init__(self, name: str):
        """ init the NameSpace with its name """
        self.name = name
        self.entries = []

    def __iter__(self):
        """ Return an iterator for the entries list """
        return iter(self.entries)
    
    def get_name(self) -> str:
        """ Simple getter method for the name of this namespace """
        return self.name

    def add_entry(self, field_name: str, typ: type, default: Any) -> Tuple[str, type, Any]:
        """ Add a new config field to this NameSpace

        The add_entry method can add a new config field to this Namespace.  A config entry consists of the name
        of the config field, its type, and its default.  Once the NameSpace is registered to the config object,
        the config object will attempt to build a config section based on this name space.  Each entry represents
        one config field that the config dictionary will look for in the properties.ini file.  If it cannot find an
        entry in the .ini file, it will use the default specified.  If the entry is found in the .ini file, then it will
        be read in and parsed into the type specified by typ.

        Parameters
        ----------
        field_name: str
            - specifies the name of the config field
        typ: type
            - specifies the type of the config field
        default: Any
            - specifies the value to use if the property is not in the application .ini file.

        Raises
        ------
        TypeError
            - When the wrong parameter types are passed to this function, or if the default value is not of the type
              specified by the typ parameter.
        ValueError
            - When the field_name is an empty string, or the field_name already exists within this namespace.

        Returns
        -------
        Tuple[str, type, Any]
            - the entry that is added to the entries list.  Note that the field_name will be converted to upper case.
        """
        err_str = f"field_name: {field_name} | typ: {typ} | default: {default}"
        NameSpace.validate_entry(field_name, typ, default)

        # Make sure that the config field hasn't already been added
        if self.has_field(field_name):
            err_msg = f"config field {field_name} already exists inside of namespace {self.name}.\ndetails - {err_str}"
            logger.error(err_msg)
            raise(ValueError(err_msg))

        # Add an entry for the given config field
        entry = (field_name.upper(), typ, default)
        self.entries.append(entry)
        return entry

    def has_field(self, field_name: str) -> bool:
        """ Check to see if the given field_name has already been added to this NameSpace
        
        Parameters
        ----------
        field_name: str
            - the field_name to search for in the NameSpace

        Returns
        -------
        bool
            - True if the field_name exists in the NameSpace, false if it does not.
        """
        search = field_name.upper()
        for entry in self.entries:
            if entry[0] == search:
                return True
        
        return False

    @staticmethod
    def validate_entry(field_name: str, typ: type, default: Any):
        """ validate a given entry for correct type and format
        
        This function performs the following checks:

        1. is the field_name a string?
        2. is the field_name not empty?
        3. is typ a type?
        4. is the default of type typ?

        if any of these questions evaluate to false, this function will raise an exception.

        Parameters
        ----------
        field_name: str
            - the name of the field
        typ: type
            - the expected type of the config field
        default: Any
            - the default to use if the field cannot be parsed

        Raises
        ------
        TypeError
            - When the wrong parameter types are passed to this function, or if the default value is not of the type
              specified by the typ parameter.
        ValueError
            - When the field_name is an empty string, or the field_name already exists within this namespace.
        """
        err_str = f"field_name: {field_name} | typ: {typ} | default: {default}"

        # Make sure the field_name is a string
        if not isinstance(field_name, str):
            err_msg = f"a config field_name must be of type string.  Instead, a {type(field_name)} was passed.\ndetails - {err_str}"
            logger.error(err_msg)
            raise TypeError(err_msg)
        
        # Make sure the field_name is not empty
        if len(field_name) == 0:
            err_msg = f"a config field_name must not be empty.\ndetails - {err_str}"
            logger.error(err_msg)
            raise ValueError(err_msg)
        
        # Make sure typ specifies a type
        if not isinstance(typ, type):
            err_msg = f"typ should be a type, specifying the type of object that the config field represents.  Instead, a {type(typ)} was passed.\ndetails - {err_str}"
            logger.error(err_msg)
            raise TypeError(err_msg)

        # Make sure the default is of type typ
        if not isinstance(default, typ):
            err_msg = f"default should be of the type specified by typ.  Instead, a {type(default)} was passed.\ndetails - {err_str}"
            logger.error(err_msg)
            raise TypeError(err_msg)