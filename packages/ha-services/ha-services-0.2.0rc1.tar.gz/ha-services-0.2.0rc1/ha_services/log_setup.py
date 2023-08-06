import logging


def basic_log_setup(*, debug: bool, format='%(asctime)s %(levelname)-8s %(message)s'):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level, format=format)
