from __future__ import annotations
import os
import yaml
import traceback
from collections import namedtuple
from backend.error.error import ConfigError
from backend.logger.logger import logger, stream_handler

file_dir = os.path.dirname(os.path.relpath(__file__))

# Definition of the static Config
Config = namedtuple('Config', (
    'host',
    'port',
    'title',
    'favicon',
    'dark',
    'debounce',
    'reconnect_timeout',
    'native',
    'window_size',
    'fullscreen',
    'frameless',
    'reload',
    'storage_secret',

    'session_time',
    'on_prem',
    'stream_handler',
    'route_timeout',
    'dicts_timeout',

    'size_fct',
    'size_min',
    'size_max',
    'table_options',
    'grid_options',

    'api_url',
    'api_key',
    'model_name',
    'model_seed',
    'model_temp',
    'model_context',
    'model_age',

    'char_limit',
    'word_limit',

    'Upload',
    'Pdf',
    'Regex',
    'Replacements'
))
# Definition of nested Upload
Upload = namedtuple('Upload', [
    'auto_upload',
    'max_files'
])
# Definition of nested Pdf
Pdf = namedtuple('Pdf', (
    'pages_per_sheet',
    'page_sep',
    'tab_size',
    'char_lim',
    'line_lim',
    'top_margin',
    'left_margin',
    'title_size',
    'font_size',
    'title_height',
    'line_height'
))
# Definition of nested Regex
Regex = namedtuple('Regex', (
    'endofs',
    'puncts',
    'begins',
    'ending',
    'digits',
    'opens',
    'close',
    'quotes'
))


def dict_to_config(config_dict: dict) -> Config:
    # Extract data and create nested sub configurations
    config_dict['Upload'] = Upload(**config_dict.pop('Upload'))
    config_dict['Pdf'] = Pdf(**config_dict.pop('Pdf'))
    config_dict['Regex'] = Regex(**config_dict.pop('Regex'))

    # Create the static configuration
    return Config(**config_dict)


def load_config(config_path: str = 'config.yml') -> Config:
    config_path = os.path.join(file_dir, config_path)
    if not os.path.isfile(config_path):
        message = f'Config file not found at "{config_path}"'
        logger.critical(message)
        raise ConfigError(message)
    try:
        with open(file = config_path, mode = 'r', encoding = 'utf-8') as file:
            config = dict_to_config(yaml.safe_load(file))
            logger.info('Config loaded')
            return config
    except Exception as exception:
        message = f'Could not parse config file with exception: {exception}\n{traceback.format_exc()}'
        logger.critical(message)
        raise ConfigError(message)


# Load the configuration
CONFIG: Config = load_config()
if not CONFIG.stream_handler:
    logger.removeHandler(stream_handler)
