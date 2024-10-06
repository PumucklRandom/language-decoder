import os
import yaml
from typing import List
from copy import deepcopy
from nicegui import ui, app
from backend.config.config import CONFIG, dict_as_object
from backend.error.error import ConfigError
from backend.logger.logger import logger

app.storage.max_tab_storage_age = CONFIG.session_time
app.add_static_file(
    local_file = os.path.join(os.path.dirname(os.path.relpath(__file__)),
                              '../../../backend/fonts/RobotoMono/RobotoMono.ttf'),
    url_path = '/fonts/RobotoMono/RobotoMono.ttf'
)


class HTML:
    FLEX_GROW = '<style>.q-textarea.flex-grow .q-field__control{height: 100%}</style>'
    RobotoMono = '''
        <style>
            @font-face{
                font-family: "RobotoMono";
                src: url('/fonts/RobotoMono/RobotoMono.ttf');
            }
        </style>
    '''


ui.add_head_html(HTML.FLEX_GROW, shared = True)
ui.add_head_html(HTML.RobotoMono, shared = True)
ui.select.default_props('outlined')
ui.input.default_props(f'dense outlined debounce="{CONFIG.debounce}"')
ui.checkbox.default_props('checked-icon=radio_button_checked unchecked-icon=radio_button_unchecked')

DEFAULT_COLS = [
    {'name': 'source', 'field': 'source', 'required': True, 'align': 'left'},
    {'name': 'target', 'field': 'target', 'required': True, 'align': 'left'},
]

DICT_COLS = deepcopy(DEFAULT_COLS)
DICT_COLS[0].update({'label': 'Source words', 'sortable': True})
DICT_COLS[1].update({'label': 'Target words', 'sortable': True})

REPLACE_COLS = deepcopy(DEFAULT_COLS)
REPLACE_COLS[0].update({'label': 'Character', 'sortable': True})
REPLACE_COLS[1].update({'label': 'Substitute', 'sortable': True})


class URLS(object):
    START = '/'
    UPLOAD = '/upload/'
    DECODING = '/decoding/'
    DICTIONARIES = '/dictionaries/'
    SETTINGS = '/settings/'
    DOWNLOAD = '/download/'


class COLORS:
    class PRIMARY:
        KEY = 'primary'
        VAL = '#409696'

    class SECONDARY:
        KEY = 'secondary'
        VAL = '#5A96E0'

    class ACCENT:
        KEY = 'accent'
        VAL = '#9632C0'

    class DARK:
        KEY = 'dark'
        VAL = '#1D1D1D'

    class DARK_PAGE:
        KEY = 'dark-page'
        VAL = '#121212'

    class POSITIVE:
        KEY = 'positive'
        VAL = '#20C040'

    class NEGATIVE:
        KEY = 'negative'
        VAL = '#C00020'

    class INFO:
        KEY = 'info'
        VAL = '#32C0E0'

    class WARNING:
        KEY = 'warning'
        VAL = '#FFFF40'

    class GREY1:
        KEY = 'grey-1'
        VAL = '#FAFAFA'

    class GREY4:
        KEY = 'grey-1'
        VAL = '#E0E0E0'

    class GREY10:
        KEY = 'grey-10'
        VAL = '#212121'

    class BLUE_GREY1:
        KEY = 'blue-grey-1'
        VAL = '#ECEFF1'

    class BLUE_GREY10:
        KEY = 'blue-grey-10'
        VAL = '#263238'

    class CYAN1:
        KEY = 'cyan-1'
        VAL = '#E0F7FA'

    class CYAN10:
        KEY = 'cyan-10'
        VAL = '#006064'


class Language(object):
    def __init__(self, dictionary):
        self.GENERAL = None
        self.START = None
        self.UPLOAD = None
        self.DECODING = None
        self.DICTIONARY = None
        self.SETTINGS = None
        self.__dict__.update(dictionary)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.__dict__.__str__()


def get_languages() -> List[str]:
    label_folder = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'labels/')
    languages = list()
    for language_file in os.listdir(label_folder):
        if language_file.endswith('.yml'):
            languages.append(os.path.splitext(language_file)[0])
    return languages


def load_language(language: str = 'english') -> Language:
    logger.info('load language')
    language_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), f'labels/{language}.yml')
    if not os.path.isfile(language_path):
        message = f'Language file not found at "{language_path}"'
        logger.critical(message)
        raise ConfigError(message)
    try:
        with open(file = language_path, mode = 'r', encoding = 'utf-8') as config_file:
            language = dict_as_object(dictionary = yaml.safe_load(config_file), object_type = Language)
            logger.info('parsed language')
            return language
    except Exception as e:
        message = f'Could not parse language file with exception:\n{e}'
        logger.critical(message)
        raise ConfigError(message)
