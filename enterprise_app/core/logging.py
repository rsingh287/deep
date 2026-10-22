import logging
import sys


def setup_logging():
    """Sets up enterprise-grade structured logging for the FastAPI app."""
    # Create logger
    logger = logging.getLogger("enterprise_app")
    logger.setLevel(logging.DEBUG)

    # Create console handler and set level to debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    logger.addHandler(ch)

    # Also log to a file
    fh = logging.FileHandler("enterprise_app.log")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


logger = setup_logging()
