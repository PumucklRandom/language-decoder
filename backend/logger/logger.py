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
file_handler = logging.FileHandler(filename = './logs/ld.log', encoding = 'utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
