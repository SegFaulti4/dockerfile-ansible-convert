import logging


def setup_custom_logger(name):

    class CustomFormatter(logging.Formatter):
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        # fmt = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
        fmt = "%(levelname)s - %(filename)s:%(lineno)d - %(message)s"

        fmts = {
            logging.DEBUG: grey + fmt + reset,
            logging.INFO: grey + fmt + reset,
            logging.WARNING: yellow + fmt + reset,
            logging.ERROR: red + fmt + reset,
            logging.CRITICAL: bold_red + fmt + reset
        }

        def format(self, record):
            log_fmt = self.fmts.get(record.levelno)
            form = logging.Formatter(log_fmt)
            return form.format(record)

    level = logging.DEBUG

    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(CustomFormatter())

    logger.addHandler(handler)
    return logger


globalLog = setup_custom_logger('global')
