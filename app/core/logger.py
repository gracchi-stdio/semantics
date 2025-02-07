import logging
import coloredlogs


def setup_logger(name: str, log_file: str, level=logging.DEBUG):
    """Set up a logger with a RotatingFileHandler."""
    log = logging.getLogger(__name__)
    # log.setLevel(level)

    # formatter = logging.Formatter(
    #     "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # )
    #
    # handler = RotatingFileHandler(
    #     log_file, maxBytes=5 * 1024 * 1024, backupCount=10
    # )  # 5 MB/log
    # handler.setFormatter(formatter)

    coloredlogs.install(level=level)
    # if not log.hasHandlers():
    # log.addHandler(handler)
    # log.addHandler(logging.StreamHandler())  # log to console too

    return log


logger = setup_logger("semantics", "logging.log")
