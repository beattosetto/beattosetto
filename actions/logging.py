
import logging
import os

LOG_FORMAT = logging.Formatter(fmt="%(asctime)s [%(processName)s]: %(levelname)s - %(message)s",
                               datefmt='%Y-%m-%d %H:%M:%S')


def setup_logger(name: str, log_file: str, mode: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup a logger with a given name and log file.
    Arguments:
        name {str} : Name of the logger.
        log_file {str} : Path to the log file.
        level {int} : Log level.
    Returns:
        The logger (logging.Logger)
    """
    try:
        handler = logging.FileHandler(log_file, mode=mode)
    except FileNotFoundError:
        try:
            # If find is not found, just create it and continue
            file = open(log_file, "a+")
            file.write(f"# Log name: {name}")
            handler = logging.FileHandler(log_file, mode=mode)
        except FileNotFoundError:
            # We cannot fix this so just reverse filename to a logger name and normally save it.
            handler = logging.FileHandler(f'{name}.log', mode=mode)
    handler.setFormatter(LOG_FORMAT)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def log_two_handler(first_logger: logging.Logger, second_logger: logging.Logger, level: int = logging.INFO, log: str = None):
    """
    Log to two loggers in a same time.
    Arguments:
        first_logger {logging.Logger} : First logger.
        second_logger {logging.Logger} : Second logger.
        level {int} : Log level.
        log {str} : Log message.
    """
    if log is not None:
        first_logger.log(level, log)
        second_logger.log(level, log)
    else:
        first_logger.log(level, "")
        second_logger.log(level, "")