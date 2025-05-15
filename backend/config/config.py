from __future__ import annotations
import os
import json
import yaml
import traceback
from copy import copy
from backend.error.error import ConfigError
from backend.logger.logger import logger, stream_handler

# A mapping dict to replace language independent characters for the source text
REPLACEMENTS = {'<<': '"', '>>': '"', '«': '"', '»': '"', '“': '"', '—': '-', '–': '-'}


class Config(object):
    on_prem: bool
    stream_handler: bool
    session_time: int
    debounce: int
    size_fct: int
    size_min: int
    size_max: int
    host: str
    port: int
    title: str
    favicon: str
    dark: bool
    reconnect_timeout: int
    native: bool
    window_size: tuple[int, int]
    fullscreen: bool
    frameless: bool
    reload: bool
    storage_secret: str
    api_url: str
    api_key: str
    model: str
    model_temp: float
    model_seed: int
    char_limit: int
    max_json_size: int
    table_options: list
    grid_options: list

    class Upload:
        word_limit: int
        max_file_size: int
        auto_upload: bool
        max_files: int

    class Pdf:
        page_sep: int
        tab_size: int
        char_lim: int
        line_lim: int
        title_size: float
        font_size: float
        width: float
        title_height: float
        header_height: float
        line_height: float

    class Regex:
        endofs: str
        puncts: str
        begins: str
        ending: str
        digits: str
        opens: str
        close: str
        quotes: str

    def __init__(self, dictionary) -> None:
        self.__dict__.update(dictionary)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.__dict__.__str__()

    def copy(self) -> Config:
        return copy(self)


def dict_as_object(dictionary: dict, object_type: type) -> type(object):
    return json.loads(json.dumps(dictionary), object_hook = object_type)


def load_config(config_path: str = 'config.yml') -> Config:
    logger.info('load config')
    config_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), config_path)
    if not os.path.isfile(config_path):
        message = f'Config file not found at "{config_path}"'
        logger.critical(message)
        raise ConfigError(message)
    try:
        with open(file = config_path, mode = 'r', encoding = 'utf-8') as file:
            config = dict_as_object(dictionary = yaml.safe_load(file), object_type = Config)
            logger.info('parsed config')
            return config
    except Exception:
        message = f'Could not parse config file with exception:\n{traceback.format_exc()}'
        logger.critical(message)
        raise ConfigError(message)


CONFIG = load_config()
if not CONFIG.stream_handler:
    logger.removeHandler(stream_handler)
