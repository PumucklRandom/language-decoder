import os
import yaml
import traceback
from collections import namedtuple
from backend.error.error import ConfigError
from backend.logger.logger import logger, stream_handler

os.environ["WEBVIEW2_USER_DATA_FOLDER"] = '.\\_internal\\webview'
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
    'files_timeout',

    'size_bias',
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
    'App',
    'Replacements',  # Replacement settings
    'Pdf_params',
    'Regex'
))
# Definition of nested Upload
Upload = namedtuple('Upload', (
    'auto_upload',
    'max_files'
))
# Definition of nested App settings
App = namedtuple('APP', (
    'dark_mode',
    'show_tips',
    'language',
    'reformatting',
    'model_name',
    'http',
    'https'
))
# Definition of nested Pdf settings
Pdf_params = namedtuple('Pdf', (
    'title_size',
    'font_size',
    'top_margin',
    'left_margin',
    'char_lim',
    'line_lim',
    'page_lim',
    'tab_size',
    'page_sep'
))
# Definition of nested Regex settings
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
    config_dict['App'] = App(**config_dict.pop('App'))
    config_dict['Pdf_params'] = Pdf_params(**config_dict.pop('Pdf_params'))
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
