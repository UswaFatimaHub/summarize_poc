import logging
import os

def setup_logger(log_file: str = "summarization.log"):
    logger = logging.getLogger("summarizer")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
