from logging import Logger, getLogger
import logging


def setup_logger(logger_tag: str, file_path: str, logging_level: str) -> Logger:
    """Setup a logger for project logging

    Args:
        logger_tag (str): The tag of the logger
        file_name (str): Where the
        logging_level (str): The level of the logger | ex. (FATAL, ERROR, WARN, INFO, DEBUG, TRACE, ALL, OFF)

    Returns:
        Logger: The logging channel that messages will be written to
    """
    # set the format for log messages
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # initialize handler
    handler = ""

    # if the file_path is None
    if file_path != None:
        # output to file
        handler = logging.FileHandler(file_path, mode="w+")
    # if the value passed to file_name IS None
    else:
        # output to stdout
        handler = logging.StreamHandler()

    # format messages
    handler.setFormatter(formatter)

    # get the logger and set logging level
    logger = getLogger(logger_tag)
    logger.setLevel(logging_level)
    logger.addHandler(handler)
    logger.propagate = True

    # return the logger
    return logger


def get_logger(logger_name: str, module_name: str) -> Logger:
    """Returns a logger

    Args:
        logger_name (str): The name of the logger
        module_name (str): The name of the module calling the function

    Returns:
        Logger: The logging channel that messages will be written to
    """
    return getLogger(logger_name).getChild(module_name)
