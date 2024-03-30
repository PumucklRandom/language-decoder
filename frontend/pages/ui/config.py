import os
import yaml
from typing import List
from copy import deepcopy
from nicegui import ui
from backend.config.config import CONFIG, dict_as_object
from backend.error.error import ConfigError
from backend.logger.logger import logger

SIZE_FACTOR = 10


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
        VAL = '#409696'  # 409696

    class SECONDARY:
        KEY = 'secondary'
        VAL = '#5A96E0'

    class ACCENT:
        KEY = 'accent'
        VAL = '#9632C0'

    class DARK:
        KEY = 'dark'
        VAL = '#1D1D1D'

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

    class GREY_1:
        KEY = 'grey-1'
        VAL = '#FAFAFA'

    class GREY_10:
        KEY = 'grey-10'
        VAL = '#212121'

    class BLUE_GREY_1:
        KEY = 'blue-grey-1'
        VAL = '#ECEFF1'

    class BLUE_GREY_10:
        KEY = 'blue-grey-10'
        VAL = '#263238'

    class CYAN_1:
        KEY = 'cyan-1'
        VAL = '#E0F7FA'

    class CYAN_10:
        KEY = 'cyan-10'
        VAL = '#006064'


class HTML:
    FLEX_GROW = '<style>.q-textarea.flex-grow .q-field__control{height: 100%}</style>'
    HEADER_STICKY = f'''
        <style lang="sass">
            .sticky-header
                max-height: 100vh
                .q-table__top,
                .q-table__bottom,
                thead tr:first-child th
                    background-color: {COLORS.PRIMARY.KEY}
                thead tr th
                    position: sticky
                    z-index: 1
                thead tr:first-child th
                    top: 0
                &.q-table--loading thead tr:last-child th
                    top: 48px
                tbody
                    scroll-margin-top: 48px
        </style>
    '''


# TODO: change default icons of ui.checkbox with radio_button_unchecked, radio_button_checked
ui.select.default_props('outlined')
ui.input.default_props(f'dense outlined debounce="{CONFIG.debounce}"')

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
