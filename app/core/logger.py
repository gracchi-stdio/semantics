import logging
import coloredlogs


def setup_logger(name: str, level=logging.DEBUG):
    """Set up a logger with a RotatingFileHandler."""
    log = logging.getLogger(name)
    log.setLevel(level)
    coloredlogs.install(level=level, logger=log)

    return log


logger = setup_logger(__name__)
