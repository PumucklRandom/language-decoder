import os
import logging
import logging.handlers
from typing import Tuple


def get_logger(log_dir: str = './logs/', log_level: int = logging.DEBUG,
               max_bytes: int = 10_240_000) -> Tuple[logging.Logger, logging.StreamHandler]:
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger('LanguageDecoder')

    if logger.handlers:
        logger.handlers.clear()

    logger.setLevel(log_level)
    formatter = logging.Formatter(
        fmt = '%(asctime)s - %(filename)s - %(levelname)s: %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.handlers.RotatingFileHandler(
        filename = os.path.join(log_dir, 'ld.log'),
        encoding = 'utf-8',
        maxBytes = max_bytes,
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger, stream_handler


logger, stream_handler = get_logger()
