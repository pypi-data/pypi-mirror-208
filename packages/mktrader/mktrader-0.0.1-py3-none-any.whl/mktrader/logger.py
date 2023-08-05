import logging

logger = logging

def set_logs(level:str) -> None:
    if level == 'debug':
        logger.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[
            logging.StreamHandler()
            ]
        )

    if level == 'info':
        logger.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[
            logging.StreamHandler()
            ]
        )

    if level == 'warning':
        logger.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[
            logging.StreamHandler()
            ]
        )

    if level == 'error':
        logger.basicConfig(
            level=logging.ERROR,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[
            logging.StreamHandler()
            ]
        )

    if level == 'critical':
        logger.basicConfig(
            level=logging.CRITICAL,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[
            logging.StreamHandler()
            ]
        )
