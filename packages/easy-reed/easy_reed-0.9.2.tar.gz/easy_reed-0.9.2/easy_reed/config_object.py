""" this module holds the core easy_reed.config.Config object

The easy_reed.config.Config object can be used to easily configure multiple python modules across
multiple environments.  When adding new config fields for your library, or for an end application,
you will define them in code via a namespace object.  When you instantiate a namespace, you will 
give it a name to identify it's fields in the config dictionary.  

Each config entry consists of a field name (str),
a type to read the field in as, and a default to use if the field is not in the config file.  Once a
namespace has been defined, it can be added to the config dictionary.  When the namespace is added to the
config dictionary, an entry for the namespace will be created in the config dictionary with all of its
config fields beneath it.  To access "field1" in namespace "app" after adding it to the config, you would type
config["app"]["field1"].

Such a field would have the following key in the config.ini - "app.field1", or {namespace.name}.{field_name}.  
field_name can have more '.' characters in it, but '.' is illegal in a namespace name since the '.' character
separates the namespace name and the field name in the config file.  Diferent sections of the config file
should represent various application environments.  Then, fields can easily be changed there across environments.
Through the addition of namespacing, library writers will be able to worry less about having field names
that conflict with other libraries.

MODULE CLASSES
--------------
Config - the core config object of the easy_reed framework.  Reads in and stores config fields.
ConfigDict - dictionary wrapper class that does not allow the __setitem__ operations - fields must be read from 
             the config file or registered via a namespace

@Author - Reed Nathaniel Schick
@DateCreated - 4/29/2023
@DateModified - 4/29/2023
"""


# Standard Library Imports
from typing import Any, Dict, Tuple, Callable

# Application Imports
from easy_reed._logger import logger
from easy_reed.namespace import NameSpace
from easy_reed.config_reader import ConfigReader
from easy_reed.environment import Environment


class ConfigDict():
    """ Object to hold a namespace's config fields once added to the config dictionary.
    
    This is a small dictionary wrapper class.  The main difference is that the ConfigDict object
    will record the name of the namespace that it represents, and it won't allow users to set
    objects directly in code.  This is an underlying utility of the Config object that should only be
    instantiated and modified through the add_namespace method of the easy_reed.config.Config object.

    INSTANCE VARIABLES
    ------------------
    _config: Dict[str, Any]
        - underlying config that holds config fields for this ConfigDict
    _name: str
        - the name of this ConfigDict, as defined by the namespace used when creating it

    METHODS
    -------
    __getitem__(self, namespace: str) -> ConfigDict
        - Returns the ConfigDict that holds entries from the given namespace
    __setitem__(self, key: str, value: Any) -> ValueError
        - Throws a ValueError - config fields must be added via a namespace.
    __iter__(self)
        - Returns an iterator for the underlying dict, allowing users to loop through each field.
    """

    def __init__(self, name):
        """ Initializes a new ConfigDict with its name taken from the given namespace """
        self._config = {}
        self._name = name

    def __getitem__(self, arg: str) -> Any:
        """ makes the object subscriptable for values from the dictionary that it wraps. """
        field = arg.upper()
        if field not in self._config:
            raise KeyError(f"{field} is missing from the config")
        return self._config[field]
    
    def __setitem__(self, key: str, value: Any) -> ValueError:
        """ Raises a ValueError - ConfigDicts should never be modified by the end user in code """
        raise ValueError("The easy_reed Config object does not allow developers to set config fields directly in code.  This must be done from a configuration file.")
    
    def __iter__(self):
        """ returns an iterator for the dictionary that this class wraps """
        return iter(self._config)

class Config():
    """ The core object of the easy_reed framework.

    The easy_reed.config.Config object can be used to easily configure multiple python modules across
    multiple environments.  When adding new config fields for your library, or for an end application,
    you will define them in code via a namespace object.  When you instantiate a namespace, you will 
    give it a name to identify it's fields in the config dictionary.  

    Each config entry consists of a field name (str),
    a type to read the field in as, and a default to use if the field is not in the config file.  Once a
    namespace has been defined, it can be added to the config dictionary.  When the namespace is added to the
    config dictionary, an entry for the namespace will be created in the config dictionary with all of its
    config fields beneath it.  To access "field1" in namespace "app" after adding it to the config, you would type
    config["app"]["field1"].

    Such a field would have the following key in the config.ini - "app.field1", or {namespace.name}.{field_name}.  
    field_name can have more '.' characters in it, but '.' is illegal in a namespace name since the '.' character
    separates the namespace name and the field name in the config file.  Diferent sections of the config file
    should represent various application environments.  Then, fields can easily be changed there across environments.
    Through the addition of namespacing, library writers will be able to worry less about having field names
    that conflict with other libraries.

    INSTANCE VARIABLES
    ------------------
    _config: dict[str, ConfigDict]
        - the underlying config dictionary that maps namespace names to a ConfigDict.
    _config_reader: ConfigReader
        - Used to in private functions to read in config fields.

    METHODS
    -------
    __getitem__(self, namespace: str) -> ConfigDict
        - Returns the ConfigDict that holds entries from the given namespace
    __setitem__(self, key: str, value: Any) -> ValueError
        - Throws a ValueError - config fields must be added via a namespace.
    __iter__(self)
        - Returns an iterator for the underlying config dict, allowing users to loop through each namespace
    add_namespace(self, namespace: NameSpace) -> None
        - Create a new ConfigDict and read all field entries from namespace into it.
    add_handler(self, typ: type, handler: Callable) -> Callable
        - Add a new handler function of type typ to the underlying ConfigReader; enables automatic string to type conversion.
    """

    def __init__(self):
        self._environment = Environment()
        self._config = {}
        self._config_reader = ConfigReader(self._environment)

    def __getitem__(self, namespace: str) -> ConfigDict:
        """ fetches the ConfigDict associated with the given namespace """
        if namespace not in self._config:
            raise KeyError(f"{namespace} is not a namespace in the Config dictionary.")
        return self._config[namespace]

    def __setitem__(self, key: str, value: Any) -> ValueError:
        """ Raises a ValueError - ConfigDicts should never be modified by the end user in code """
        raise ValueError("The easy_reed Config object does not allow developers to set config fields directly in code.  This must be done from a configuration file.")
    
    def __iter__(self):
        """ returns an iterator for the _config instance variable """
        return iter(self._config)
    
    def add_namespace(self, namespace: NameSpace) -> None:
        """ Add a new namespace to the config dictionary and read in its fields.

        In order to add new config fields to the easy_reed.config.Config object, you will need to define an
        easy_reed.namespace.NameSpace object and register it here.  When you create a namespace, you give a name
        for that namespace.  That name will be used as a key in the _config instance variable for a ConfigDict
        holding all of its fields.  Once you have defined and added all of the field names, types, and defaults to
        the NameSpace, the NameSpace will be passed here to be set up in the config dictionary.

        This function will create the new ConfigDict and set its name.  Then, For each field under the namespace, 
        this function will add an entry in the ConfigDict.  If the field is present in the end user's .ini file,
        then the value given by the user will be read in and stored for later use.  If it does not exist in the .ini file, 
        then the default given to the namespace will be used instead.

        Once a namespace has been added, this function will throw an error if a namespace with the same name gets passed to
        this function, regardless of whether or not the fields under it are new.  Therefore, all fields for a config namespace
        must be defined exactly once before the namespace is added to the config dict.  If the .ini file has multiple sections,
        then this class will pull values from the section specified by the "APP_ENVIRONMENT" environment variable.

        Parameters
        ----------
        namespace: Namespace
            - the namespace being added to this Config object

        Raises
        ------
        ValueError
            - when the namespace already exists inside of the Config object.
        TypeError  
            - when any field in the namespace specifies a type that the Config Reader cannot handle.

        Returns
        -------
        None
        """
        logger.debug(f"Attempting to add namespace {namespace.get_name()} to the config dictionary.")

        # Make sure the current namespace does not exist in the config
        if namespace.get_name() in self._config:
            msg = f"ERROR - namespace {namespace.get_name()} already exists inside of the config dictionary."
            logger.error(msg)
            raise ValueError(msg)
        
        # Create a new ConfigDict to hold fields defined by the namespace
        self._config[namespace.get_name()] = ConfigDict(namespace.get_name())

        # Read each namespace entry into the new ConfigDict using the ConfigReader object
        for entry in namespace:
            self._config[namespace.get_name()]._config[entry[0]] = self._config_reader.read_field(f"{namespace.get_name()}.{entry[0]}",entry[1],entry[2])
        
        logger.debug(f"finished adding config namespace {namespace.get_name()} to the Config.")

    def add_handler(self, typ: type, handler: Callable) -> Callable:
        """ Adds a new type handler for parsing type typ
        
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
        return self._config_reader.add_handler(typ, handler)