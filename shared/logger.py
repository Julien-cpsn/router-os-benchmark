import logging
import sys
import time


def setup_logger(target: str, verbosity: int) -> logging.Logger:
    """
    Set up logging configuration.

    :return: Configured logger
    """
    verbosity_options = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }

    logger = logging.getLogger(target)
    logger.setLevel(verbosity_options[verbosity])
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s | %(levelname)s | %(name)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def get_time(number_tests: int, number_runs: int, duration: int) -> str:
    test_seconds = number_tests * number_runs * (duration+2)
    test_time = time.strftime('%H:%M:%S', time.gmtime(test_seconds))

    return test_time