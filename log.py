import logging


def setup_custom_logger(name):
    fmt = "%(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    level = logging.DEBUG

    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt))

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.propagate = False

    logger.addHandler(handler)
    return logger


globalLog = setup_custom_logger('global')
