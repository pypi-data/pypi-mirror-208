import easy_reed.environment
import easy_reed.namespace
import easy_reed.config_reader
import easy_reed.config_object
import easy_reed._logger

logger = easy_reed._logger.logger
config = easy_reed.config_object.Config()

logger.debug("Here")

config._config["easy_reed"] = easy_reed.config_object.ConfigDict("easy_reed")
easy_reed_config = config._config["easy_reed"]._config
easy_reed_config[easy_reed.environment.Environment._log_level_key] = config._environment.get_log_level()
easy_reed_config[easy_reed.environment.Environment._app_environment_key] = config._environment.get_app_environment()
easy_reed_config[easy_reed.environment.Environment._config_location_key] = config._environment.get_config_location()
easy_reed_config["LOG_LOCATION"] = easy_reed._logger.LOG_LOCATION
