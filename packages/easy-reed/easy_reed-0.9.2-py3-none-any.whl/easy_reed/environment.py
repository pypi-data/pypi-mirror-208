""" Environment module - responsible for retrieving optional startup values from the current working environment

The core of this module is the 'Environment' class.  It is responsible for reading in details from os.environ.
There are three values that this class will look for
    1. LOG_LEVEL
        - This key should specify which log calls to log.  While this can be set in the config ini file, there are log messages
          that will print during environment initialization.  By default, the log level is set to 'DEBUG' until the property can
          be loaded from the .ini file.  If you want to turn off these initialization logs, set this value to 'INFO'.
        - EXAMPLES: 'INFO' 'WARNING' 'ERROR' 'DEBUG'
    2. APP_ENVIRONMENT
        - This key will tell the config dictionary the properties section it should read from.  You may want to set config fields to 
          unique values in different environments.  Maybe the log level in 'dev' is 'DEBUG' while in 'prod' its 'INFO'
        - EXAMPLES: 'DEV' 'QA' 'PROD'
    3. CONFIG_LOCATION
        - This key will specify where the config object should look for the application level settings in a deployment.  by default, 
          the config file is expected to be in "properties_config.ini".  You can change that default here.
        - EXAMPLES: "config.ini" "properties.ini" 

MODULE CLASSES
---------------
Environment - responsible for reading in the current application environment.  These details inform the config setup.

@Author - Reed Nathaniel Schick
@DateCreated - 4/26/2023
@DateModified - 4/26/2023
"""


# Standard Library Imports
import os, logging

# Application Imports
from easy_reed._logger import logger

class Environment():
    """ responsible for reading in the current application environment.  These details inform the config setup.
    
    the 'Environment' class  is responsible for reading in details from os.environ.
    There are three values that this class will look for
    1. LOG_LEVEL
        - This key should specify which log calls to log.  While this can be set in the config ini file, there are log messages
          that will print during environment initialization.  By default, the log level is set to 'DEBUG' until the property can
          be loaded from the .ini file.  If you want to turn off these initialization logs, set this value to 'INFO'.
        - EXAMPLES: 'INFO' 'WARNING' 'ERROR' 'DEBUG'
    2. APP_ENVIRONMENT
        - This key will tell the config dictionary the properties section it should read from.  You may want to set config fields to 
          unique values in different environments.  Maybe the log level in 'dev' is 'DEBUG' while in 'prod' its 'INFO'
        - EXAMPLES: 'DEV' 'QA' 'PROD'
    3. CONFIG_LOCATION
        - This key will specify where the config object should look for the application level settings in a deployment.  by default, 
          the config file is expected to be in "properties_config.ini".  You can change that default here.
        - EXAMPLES: "config.ini" "properties.ini" 
    """

    _log_level_key = "LOG_LEVEL"
    _app_environment_key = "APP_ENVIRONMENT"
    _config_location_key = "CONFIG_LOCATION"

    _app_environment_default = "local"
    _app_config_location_default = "properties_config.ini"
    _log_level_default = "DEBUG"

    def __init__(self):
        # Retrieve the log level from the environment if available, and log it out
        self._log_level = Environment._retrieve_key(Environment._log_level_key, Environment._log_level_default)
        try:
            logger.setLevel(self._log_level.upper())
        except ValueError as e:
            logger.error(f"ERROR: LOG_LEVEL read in as {self._log_level}, but this is not a valid log level.  Defaulting to {Environment._log_level_default}")
            logger.setLevel(Environment._log_level_default)
        logger.debug(f"{Environment._log_level_key} set to {self._log_level}")
        # Retrieve the app environment from the environment if available, and log it out
        self._app_environment = Environment._retrieve_key(Environment._app_environment_key, Environment._app_environment_default)
        logger.debug(f"{self._app_environment_key} set to {self._app_environment}")
        # Retrieve the config location from the environment if available, and log it out
        self._app_config_location = Environment._retrieve_key(Environment._config_location_key, Environment._app_config_location_default)
        logger.debug(f"APP_CONFIG_LOCATION set to {self._app_config_location}")

    def get_log_level(self) -> str:
        """ return the log_level, as read in from os.environ """
        return self._log_level

    def get_app_environment(self) -> str:
        """ return the app_environment, as read in from os.environ """
        return self._app_environment

    def get_config_location(self) -> str:
        """ return the config_location, as read in from os.environ """
        return self._app_config_location
    
    @staticmethod
    def _retrieve_key(env_key, default) -> str:
        """ Internal method used to fetch environment values.  Provides a default when values can't be found """
        if env_key not in os.environ:
            logger.error(f"{env_key} is not present in the current environment.  Defaulting {env_key} to {default}")
        
        return os.environ.get(env_key, default)
    