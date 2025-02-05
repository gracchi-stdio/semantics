

import logging
from cgitb import handler
from  logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """Set up a logger with a RotatingFileHandler."""
    log = logging.getLogger(name)
    log.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=10) # 5 MB/log
    handler.setFormatter(formatter)

    if not log.hasHandlers():
        log.addHandler(handler)
        log.addHandler(logging.StreamHandler()) # log to console too

    return log

logging.getLogger("semantics").setLevel(logging.DEBUG) # change to debug

logger = setup_logger("semantics", "logging.log")