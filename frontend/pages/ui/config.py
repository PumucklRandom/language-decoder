import os
import yaml
import traceback
from copy import deepcopy
from nicegui import ui, app
from collections import namedtuple
from backend.error.error import UIConfigError
from backend.config.config import CONFIG
from backend.logger.logger import logger

file_dir = os.path.dirname(os.path.relpath(__file__))

# app.native.window_args['background_color'] = COLORS.DARK_PAGE.VAL
# app.native.start_args['private_mode'] = True
# app.native.start_args['storage_path'] = '.\\_internal\\pywebview'
# app.native.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True
app.native.settings['ALLOW_DOWNLOADS'] = CONFIG.native
app.storage.max_tab_storage_age = CONFIG.session_time
app.add_static_file(
    local_file = os.path.join(file_dir, '../../../backend/fonts/RobotoMono/RobotoMono.ttf'),
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

# Static URLS for each page
Urls = namedtuple(
    'Urls', ('START', 'UPLOAD', 'DECODING', 'DICTIONARIES', 'SETTINGS', 'DOWNLOAD')
)
URLS = Urls(
    START = '/',
    UPLOAD = '/upload/',
    DECODING = '/decoding/',
    DICTIONARIES = '/dictionaries/',
    SETTINGS = '/settings/',
    DOWNLOAD = '/download/'
)

# List of all static colors
Color = namedtuple('Color', ('KEY', 'VAL'))
PRIMARY = Color('primary', '#409696')
SECONDARY = Color('secondary', '#5A96E0')
ACCENT = Color('accent', '#9632C0')
DARK = Color('dark', '#1D1D1D')
DARK_PAGE = Color('dark-page', '#121212')
POSITIVE = Color('positive', '#20C040')
NEGATIVE = Color('negative', '#C00020')
INFO = Color('info', '#32C0E0')
WARNING = Color('warning', '#FFFF40')
ORANGE = Color('orange', '#FF6000')
GREY1 = Color('grey-1', '#FAFAFA')
GREY4 = Color('grey-4', '#E0E0E0')
GREY10 = Color('grey-10', '#212121')
BLUE_GREY1 = Color('blue-grey-1', '#ECEFF1')
BLUE_GREY10 = Color('blue-grey-10', '#263238')
PRIME_DARK = Color('prime-dark', '#204848')
PRIME_LIGHT = Color('prime-light', '#A0DEDE')

Colors = namedtuple(
    'Colors', ('PRIMARY', 'SECONDARY', 'ACCENT', 'DARK', 'DARK_PAGE', 'POSITIVE', 'NEGATIVE', 'INFO', 'WARNING',
               'ORANGE', 'GREY1', 'GREY4', 'GREY10', 'BLUE_GREY1', 'BLUE_GREY10', 'PRIME_DARK', 'PRIME_LIGHT')
)

COLORS = Colors(
    PRIMARY = PRIMARY,
    SECONDARY = SECONDARY,
    ACCENT = ACCENT,
    DARK = DARK,
    DARK_PAGE = DARK_PAGE,
    POSITIVE = POSITIVE,
    NEGATIVE = NEGATIVE,
    INFO = INFO,
    WARNING = WARNING,
    ORANGE = ORANGE,
    GREY1 = GREY1,
    GREY4 = GREY4,
    GREY10 = GREY10,
    BLUE_GREY1 = BLUE_GREY1,
    BLUE_GREY10 = BLUE_GREY10,
    PRIME_DARK = PRIME_DARK,
    PRIME_LIGHT = PRIME_LIGHT
)


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


ui.add_head_html(
    code = '''
        <style>
            .table-bottom-space .q-table__middle {
                padding-bottom: 15px;
            }
        </style>
    ''',
    shared = True
)

ui.add_head_html(
    code = '''
        <style>
             .q-textarea.flex-grow .q-field__control{
                 height: 100%;
             }
        </style>
    ''',
    shared = True
)
ui.add_head_html(
    code = '''
        <style>
            @font-face{
                 font-family: "RobotoMono";
                 src: url('/fonts/RobotoMono/RobotoMono.ttf');
            }
        </style>
    ''',
    shared = True
)
ui.add_head_html(
    code = '''
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
    ''',
    shared = True
)

ui.header.default_style('height:66px')  # align-items:center
ui.footer.default_style('height:66px')  # align-items:center
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


# Definition of the page labels
UILabels = namedtuple(
    'UILabels', ('GENERAL', 'START', 'UPLOAD', 'DECODING', 'DICTIONARY', 'SETTINGS'),
)


def dict_to_labels(labels_dict: dict) -> UILabels:
    return UILabels(
        GENERAL = to_labels("GENERAL", labels_dict.pop("GENERAL")),
        START = to_labels("START", labels_dict.pop("START")),
        UPLOAD = to_labels("UPLOAD", labels_dict.pop("UPLOAD")),
        DECODING = to_labels("DECODING", labels_dict.pop("DECODING")),
        DICTIONARY = to_labels("DICTIONARY", labels_dict.pop("DICTIONARY")),
        SETTINGS = to_labels("SETTINGS", labels_dict.pop("SETTINGS"))
    )


def to_labels(name: str, sub_tree: any):
    if isinstance(sub_tree, dict):
        return namedtuple(name, sub_tree.keys())(
            **{_name: to_labels(_name, _sub_tree) for _name, _sub_tree in sub_tree.items()}
        )
    elif isinstance(sub_tree, list):
        return tuple(sub_tree)
    return sub_tree


def load_labels(language: str = 'english') -> UILabels:
    language_path = os.path.join(file_dir, f'labels/{language}.yml')
    if not os.path.isfile(language_path):
        message = f'UI Labels file not found at "{language_path}"'
        logger.critical(message)
        raise UIConfigError(message)
    try:
        with open(file = language_path, mode = 'r', encoding = 'utf-8') as file:
            labels = dict_to_labels(yaml.safe_load(file))
            logger.info('UI labels loaded')
            return labels
    except Exception as exception:
        message = f'Could not parse UI labels file with exception: {exception}\n{traceback.format_exc()}'
        logger.critical(message)
        raise UIConfigError(message)


def get_languages() -> list[str]:
    languages = list()
    labels_path = os.path.join(file_dir, 'labels/')
    for language_file in os.listdir(labels_path):
        if os.path.isfile(os.path.join(labels_path, language_file)) and language_file.endswith('.yml'):
            languages.append(os.path.splitext(language_file)[0])
    return languages


ui_labels_cache: dict[str, UILabels] = dict()


def get_ui_labels(language: str = 'english') -> UILabels:
    if language in ui_labels_cache:
        return ui_labels_cache.get(language)
    try:
        ui_labels_cache[language] = load_labels(language)
        return ui_labels_cache.get(language)
    except UIConfigError:
        return ui_labels_cache.get('english')


UI_LABELS: UILabels = get_ui_labels()
