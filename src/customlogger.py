import inspect
import logging
from src.configs import configurations
from pathlib import Path
import os

def custom_logger():
    # For getting the class/ method name from where the logger is called
    log_name = inspect.stack()[1][3]

    # Logger object with log name as parameter
    logger = logging.getLogger(log_name)

    # Set the log level
    logger.setLevel(logging.DEBUG)

    # Create file handler to save the logs in a file
    if os.path.exists("logs"):
        log_file = configurations.get_relative_path("logs", "test_logs.log")
        file_handler = logging.FileHandler(log_file, mode='a')
    else:
        os.mkdir("logs")
        log_file = Path("logs", "test_logs.log")
        file_handler = logging.FileHandler(log_file, mode='a')

    # Set the log level for the file handler
    file_handler.setLevel(logging.DEBUG)

    # Define the format for the logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s', datefmt='%d%m%y %I:%M:%S %p %A')

    # Define formatter for fileHandler
    file_handler.setFormatter(formatter)

    # Add file handler to logging
    logger.addHandler(file_handler)

    return logger
