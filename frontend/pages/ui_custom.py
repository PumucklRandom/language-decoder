import os
import json
from typing import List
from nicegui import ui
from backend.config.const import dict_as_object

SIZE_FACTOR = 10


class Language(object):
    def __init__(self, dictionary):
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


def load_language(language: str = 'english') -> type(Language):
    language_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), f'labels/{language}.json')
    if not os.path.isfile(language_path):
        # TODO: Error Handling
        pass
    with open(language_path, 'r') as config_file:
        return dict_as_object(dictionary = json.load(config_file), object_type = Language)


def get_languages() -> List[str]:
    label_folder = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'labels')
    languages = list()
    for language_file in os.listdir(label_folder):
        if language_file.endswith('.json'):
            languages.append(os.path.splitext(language_file)[0])
    return languages


ui_language = load_language()

# TODO: change default icons of ui.checkbox
ui.select.default_props('outlined')
ui.input.default_props('dense outlined debounce="200"')


def ui_dialog(label_list: List[str]) -> ui.dialog:
    with ui.dialog() as dialog:
        with ui.card():
            ui.button(icon = 'close', on_click = dialog.close) \
                .classes('absolute-top-right') \
                .props('dense round size=12px')
            ui.space()
            for label in label_list:
                ui.label(label)
    return dialog


def abs_top_center(top: int = 0, left: int = 50) -> str:
    """
    :param top: absolute distance from top in px
    :param left: absolute distance from left in %
    """
    return f'absolute left-[{left}%] top-[{top}px] translate-x-[-50%] translate-y-[0px]'


def rel_top_center(top: int = 0, left: int = 50) -> str:
    """
    :param top: absolute distance from top in %
    :param left: absolute distance from left in %
    """
    return f'absolute left-[{left}%] top-[{top}%] translate-x-[-50%] translate-y-[-50%]'


def abs_top_left(top: int = 0, left: int = 0) -> str:
    """
    :param top: absolute distance from top in px
    :param left: absolute distance from left in px
    """
    return f'absolute left-[{left}px] top-[{top}px] translate-x-[-50%] translate-y-[0px]'


def rel_top_abs_left(top: int = 0, left: int = 0) -> str:
    """
    :param top: absolute distance from top in %
    :param left: absolute distance from left in px
    """
    return f'absolute left-[{left}px] top-[{top}%] translate-x-[-50%] translate-y-[-50%]'


def table_item(input_size: int) -> str:
    return f'''
        <div class="column" style="width:{input_size}px; height:70px" :props="props">
            <div class="col">
                <q-input v-model="props.row.source" dense outlined debounce="200" bg-color=grey-10
                @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
            </div>
            <div class="col-xl-7">
                <q-input v-model="props.row.target" dense outlined debounce="200" bg-color=blue-grey-10
                @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
            </div>
        </div>
    '''


class COLORS:
    PRIMARY = '#409696'  # 5898D4 #80C8C8
    SECONDARY = '#5A96E0'  # 26A69A
    ACCENT = '#9632C0'  # 9C27B0
    DARK = '#1D1D1D'  # 1D1D1D
    POSITIVE = '#20C040'  # 21BA45
    NEGATIVE = '#C00020'  # C10015
    INFO = '#32C0E0'  # 31CCEC
    WARNING = '#FFFF40'  # F2C037


class HTML:
    FLEX_GROW = '<style>.q-textarea.flex-grow .q-field__control{height: 100%}</style>'
    HEADER_STICKY = '''
        <style lang="sass">
            .sticky-header
                max-height: 100vh
                .q-table__top,
                .q-table__bottom,
                thead tr:first-child th
                    background-color: #00b4ff
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


class TABLE:
    HEADER = '''
        <q-tr style="background-color:#409696" :props="props">
            <q-th v-for="col in props.cols" :key="col.field" :props="props">
                {{ col.label }}
            </q-th>
            <q-th auto-width>
                <q-btn icon="add" size="12px" dense round color="primary" :props="props"
                @click="() => $parent.$emit('_add_row')"/>
                <!-- <q-tooltip> add row below </q-tooltip> -->
            </q-th>
        </q-tr>
    '''
    BODY = '''
        <q-tr :props="props">
            <q-td key="key" style="background-color:#242A30" :props="props">
                <q-input v-model="props.row.key" dense borderless debounce="200"
                @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
            </q-td>
            <q-td key="val" style="background-color:#004840" :props="props">
                <q-input v-model="props.row.val" dense borderless debounce="200"
                @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
            </q-td>
            <q-td auto-width style="background-color:#204848">
                <div class="col">
                    <q-btn icon="remove" size="8px" dense round color="primary"
                    @click="() => $parent.$emit('_del_row', props.row)" :props="props"/>
                    <!-- <q-tooltip> delete row </q-tooltip> -->
                </div>
                <div class="col">
                    <q-btn icon="add" size="8px" dense round color="primary"
                    @click="() => $parent.$emit('_add_row', props.row)" :props="props"/>
                    <!-- <q-tooltip> add row below </q-tooltip> -->
                </div>
            </q-td>
        </q-tr>
    '''


class LIST:
    BODY = '''
        <q-tr :props="props">
            <q-td key="key" :props="props">
                {{ props.row.key }}
                <q-input v-model="props.row.val" type="number" dense outlined debounce="200"
                @update:model-value="() => $parent.$emit('_upd_param', props.row)"/>
            </q-td>
        </q-tr>
    '''
