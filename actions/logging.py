import logging


FORMAT = "%(asctime)s [%(processName)s]: %(levelname)s - %(message)s"
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def set_logger(name, first_logger_location, second_logger_location, first_logger_level, second_logger_level):
    logger = logging.getLogger(name)
    logger.setLevel(first_logger_level)

    formatter = logging.Formatter(FORMAT, TIME_FORMAT)

    # build and add main handler
    file_handler = logging.FileHandler(first_logger_location)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # build and add sub handler
    file_handler = logging.FileHandler(second_logger_location)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(second_logger_level)
    logger.addHandler(file_handler)

    return logger
