import os
import yaml
import json
from backend.error.error import ConfigError
from backend.logger.logger import logger

DECODE_COLS = [
    {'name': 'source', 'field': 'source', 'required': True, 'align': 'left'},
    {'name': 'target', 'field': 'target', 'required': True, 'align': 'left'},
]

DICT_COLS = [
    {'label': 'Source Words', 'name': 'key', 'field': 'key', 'required': True, 'sortable': True, 'align': 'left'},
    {'label': 'Target Words', 'name': 'val', 'field': 'val', 'required': True, 'sortable': True, 'align': 'left'},
]

REPLACE_COLS = [
    {'label': 'Character ', 'name': 'key', 'field': 'key', 'required': True, 'sortable': True, 'align': 'left'},
    {'label': 'Substitute', 'name': 'val', 'field': 'val', 'required': True, 'sortable': True, 'align': 'left'},
]

PDF_COLS = [
    {'name': 'key', 'field': 'key', 'required': True, 'align': 'left'},
    {'name': 'val', 'field': 'val', 'required': True, 'align': 'left'},
]
# A mapping dict to replace language independent characters for the source text
REPLACEMENTS = {'<<': '"', '>>': '"', '«': '"', '»': '"', '“': '"', '—': '-', '–': '-'}

# Character mark patterns for reformation of the source text
PUNCTUATIONS = '.!?'
BEG_PATTERNS = '#$<(\[{'
END_PATTERNS = ',;.:!?°%€>)\]}'
QUO_PATTERNS = '"\'´`'


class URLS(object):
    START = '/'
    UPLOAD = '/upload/'
    DECODING = '/decoding/'
    DICTIONARIES = '/dictionaries/'
    SETTINGS = '/settings/'
    DOWNLOAD = '/download/'


class Config(object):
    def __init__(self, dictionary) -> None:
        self.__dict__.update(dictionary)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.__dict__.__str__()


def dict_as_object(dictionary: dict, object_type: type(object)) -> object:
    return json.loads(json.dumps(dictionary), object_hook = object_type)


def load_config(config_path: str = 'config.yml') -> type(Config):
    logger.info('load config')
    config_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), config_path)
    if not os.path.isfile(config_path):
        message = f'Config file not found at "{config_path}"'
        logger.critical(message)
        raise ConfigError(message)
    try:
        with open(config_path, 'r') as config_file:
            config = dict_as_object(dictionary = yaml.safe_load(config_file), object_type = Config)
            logger.info('parsed config')
            return config
    except Exception as exception:
        message = f'Could not parse config file with exception:\n{exception}'
        logger.critical(message)
        raise ConfigError(message)


CONFIG = load_config()
