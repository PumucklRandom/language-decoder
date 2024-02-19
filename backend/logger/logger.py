import logging

logger = logging.getLogger('LanguageDecoder')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt = '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S'
)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
