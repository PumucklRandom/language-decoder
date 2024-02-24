import os
import logging

if not os.path.isdir('./logs/'):
    os.makedirs('./logs/')

logger = logging.getLogger('LanguageDecoder')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt = '%(asctime)s - %(filename)s - %(levelname)s: %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S'
)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('./logs/ld.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
