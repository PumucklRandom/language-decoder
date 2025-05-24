import os
import yaml
from copy import deepcopy
from nicegui import ui, app
from backend.config.config import CONFIG, dict_as_object
from backend.error.error import ConfigError
from backend.logger.logger import logger

# app.native.window_args['background_color'] = COLORS.DARK_PAGE.VAL
# app.native.start_args['private_mode'] = True
# app.native.start_args['storage_path'] = '.\\_internal\\pywebview'
app.native.settings['ALLOW_DOWNLOADS'] = CONFIG.native
# app.native.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True
app.storage.max_tab_storage_age = CONFIG.session_time
app.add_static_file(
    local_file = os.path.join(os.path.dirname(os.path.relpath(__file__)),
                              '../../../backend/fonts/RobotoMono/RobotoMono.ttf'),
    url_path = '/fonts/RobotoMono/RobotoMono.ttf'
)

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


class URLS:
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

    class ORANGE:
        KEY = 'red-orange'
        VAL = '#FF6000'

    class GREY1:
        KEY = 'grey-1'
        VAL = '#FAFAFA'

    class GREY4:
        KEY = 'grey-4'
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


class JS:
    FOCUS_INPUT = '''
        setTimeout(function() {
            const findInput = document.querySelector('.q-menu input[aria-label="find"]');
            if (findInput) {
                findInput.focus();
                findInput.select();
            }
        }, 0);
    '''

    DEL_OBSERVER = '''
        if (window.cellObserver) {
            window.cellObserver.disconnect();
            window.cellObserver = null;
        }
    '''

    CLEAR_CELLS = f'''
        function clearCells() {{
            const inputs = document.querySelectorAll(".q-table__grid-content input");
            for (const input of inputs) {{
                input.style.color = "";
            }}
        }}
        clearCells();
        {DEL_OBSERVER}
    '''

    @classmethod
    def mark_cells(cls, find_str: str) -> str:
        return f'''
            // Function to mark cells
            function markCells(find_str) {{
                const inputs = document.querySelectorAll(".q-table__grid-content input");
                for (const input of inputs) {{
                    if (input.value && input.value.includes(find_str)) {{
                        input.style.color = "{COLORS.ORANGE.VAL}";
                    }} else {{
                        input.style.color = "";
                    }}
                }}
            }}
            markCells("{find_str}");
            {cls.DEL_OBSERVER}
            // Observer to detect changes in cells
            window.cellObserver = new MutationObserver(function(mutations) {{
                for (const mutation of mutations) {{
                    if (mutation.type === "childList") {{
                        markCells("{find_str}");
                        break;
                    }}
                }}
            }});
            // const gridTable = document.querySelector(".q-table__grid-content");
            window.cellObserver.observe(document.body, {{ childList: true, subtree: true }});
        '''


ui.add_head_html(code = '''
                     <style>
                         .q-textarea.flex-grow .q-field__control{
                             height: 100%;
                         }
                     </style>
                 ''', shared = True)
ui.add_head_html(code = '''
                     <style>
                         @font-face{
                             font-family: "RobotoMono";
                             src: url('/fonts/RobotoMono/RobotoMono.ttf');
                         }
                     </style>
                 ''', shared = True)
ui.add_head_html(code = '''
                     <style>
                         .sticky-header q-table__top,
                         .sticky-header thead tr th {
                             position: sticky;
                             z-index: 1;
                         }
                         .sticky-header thead tr:first-child th {
                             top: 0;
                         }
                     </style>
                 ''', shared = True)
ui.input.default_props(f'dense outlined debounce="{CONFIG.debounce}"')
ui.checkbox.default_props('checked-icon=radio_button_checked unchecked-icon=radio_button_unchecked')


def top_left(top: int = 0, left: int = 0, u_top: str = 'px', u_left: str = 'px', center: bool = False) -> str:
    """
    :param top: distance from top
    :param left: distance from left
    :param u_top: unit for top in px or %
    :param u_left: unit for left in px or %
    :param center: using center of ui
    """
    if not center:
        return f'absolute top-[{top}{u_top}] left-[{left}{u_left}]'
    return f'absolute top-[{top}{u_top}] left-[{left}{u_left}] translate-y-[-50%] translate-x-[-50%]'


def top_right(top: int = 0, right: int = 0, u_top: str = 'px', u_right: str = 'px', center: bool = False) -> str:
    """
    :param top: distance from top
    :param right: distance from right
    :param u_top: unit for top in px or %
    :param u_right: unit for right in px or %
    :param center: using center of ui
    """
    if not center:
        return f'absolute top-[{top}{u_top}] right-[{right}{u_right}]'
    return f'absolute top-[{top}{u_top}] right-[{right}{u_right}] translate-y-[-50%] translate-x-[+50%]'


def bot_left(bot: int = 0, left: int = 0, u_bot: str = 'px', u_left: str = 'px', center: bool = False) -> str:
    """
    :param bot: distance from bottom
    :param left: distance from left
    :param u_bot: unit for bottom in px or %
    :param u_left: unit for left in px or %
    :param center: using center of ui
    """
    if not center:
        return f'absolute bottom-[{bot}{u_bot}] left-[{left}{u_left}]'
    return f'absolute bottom-[{bot}{u_bot}] left-[{left}{u_left}] translate-y-[+50%] translate-x-[-50%]'


def bot_right(bot: int = 0, right: int = 0, u_bot: str = 'px', u_right: str = 'px', center: bool = False) -> str:
    """
    :param bot: distance from bottom
    :param right: distance from right
    :param u_bot: unit for bottom in px or %
    :param u_right: unit for right in px or %
    :param center: using center of ui
    """
    if not center:
        return f'absolute bottom-[{bot}{u_bot}] right-[{right}{u_right}]'
    return f'absolute bottom-[{bot}{u_bot}] right-[{right}{u_right}] translate-y-[+50%] translate-x-[+50%]'


class Language:
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


def get_languages() -> list[str]:
    labels_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'labels/')
    languages = list()
    for language_file in os.listdir(labels_path):
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
        with open(file = language_path, mode = 'r', encoding = 'utf-8') as file:
            language = dict_as_object(dictionary = yaml.safe_load(file), object_type = Language)
            logger.info('parsed language')
            return language
    except Exception as e:
        message = f'Could not parse language file with exception:\n{e}'
        logger.critical(message)
        raise ConfigError(message)
