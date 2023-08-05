""" initializes the logger for the easy_reed library.  This logger can be used by end users.

Log set up can be modified through the following environment variables.
    1. LOG_LEVEL - tells the app on startup what log_level to use at startup. "DEBUG" by default.
    2. LOG_HANDLER - a list of which handlers to use.  "[FILE, STREAM]" by default (The only two options).
    3. LOG_LOCATION - where to write logs to if there is a FILE handler.  "logs" by default.
"""
# Standard Library Imports
import logging, os
from datetime import date

# Optional logging config via environment variables
LOG_LOCATION = os.environ.get("LOG_LOCATION", default="")

# Define the log and date format for the log handlers, and create a Formatter
log_format = f'%(levelname)s | %(asctime)s | {__name__} | line %(lineno)d | %(message)s'
date_format = '%m/%d/%Y %I:%M:%S %p'
formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

# Initialize the stream and file handlers - we will attach these to the logger
stream_handler = logging.StreamHandler()
# file_handler = logging.FileHandler(filename=f'logs/{date.today()}-logs.txt')

# set the formatter for the handlers to the one created above
stream_handler.setFormatter(formatter)
# file_handler.setFormatter(formatter)

# create the logger and add the details
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
# if LOG_LOCATION != "":
#     if not os.path.exists(LOG_LOCATION):
#         os.mkdir(LOG_LOCATION)
#     logger.addHandler(file_handler)