import logging

def setup_logger(name=__name__, level=logging.INFO):
    """
    Sets up and returns a logger with the specified name and logging level.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger

def safe_run(func, *args, **kwargs):
    """
    Executes a function with provided arguments, logs and re-raises any exceptions.
    """
    logger = logging.getLogger(func.__name__)
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in function {func.__name__}: {e}")
        raise
