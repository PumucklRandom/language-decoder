from typing import Union, Tuple, Dict, List, Iterable
from nicegui import ui, events
from backend.config.config import CONFIG

DEFAULT_COLS = [
    {'name': 'key', 'field': 'key', 'required': True, 'align': 'left'},
    {'name': 'val', 'field': 'val', 'required': True, 'align': 'left'},
]

DICT_COLS = DEFAULT_COLS.copy()
DICT_COLS[0].update({'label': 'Source Words', 'sortable': True})
DICT_COLS[1].update({'label': 'Target Words', 'sortable': True})

REPLACE_COLS = DEFAULT_COLS.copy()
REPLACE_COLS[0].update({'label': 'Character', 'sortable': True})
REPLACE_COLS[1].update({'label': 'Substitute', 'sortable': True})


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
                    background-color: #409696
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


class Table(ui.table):

    def __init__(self, columns: List[Dict] = None, rows: List[Dict] = None, row_key: str = 'id') -> None:
        if columns is None:
            columns = DEFAULT_COLS
        if rows is None:
            rows = []
        super().__init__(columns = columns, rows = rows, row_key = row_key)
        self.on('_upd_row', self._upd_row)
        self.on('_del_row', self._del_row)
        self.on('_add_row', self._add_row)

    def _add_row(self, event: events.GenericEventArguments) -> None:
        _id = max([row.get('id') for row in self.rows] + [-1]) + 1
        if event.args:
            for i, row in enumerate(self.rows):
                if row.get('id') == event.args.get('id'):
                    self.rows.insert(i + 1, {'id': _id, 'key': '', 'val': ''})
        else:
            self.rows.insert(0, {'id': _id, 'key': '', 'val': ''})
        self.update()

    def _del_row(self, event: events.GenericEventArguments) -> None:
        self.rows[:] = [row for row in self.rows if row.get('id') != event.args.get('id')]
        self.update()

    def _upd_row(self, event: events.GenericEventArguments) -> None:
        for row in self.rows:
            if row.get('id') == event.args.get('id'):
                row.update(event.args)

    def load_table(self, keys: Union[Dict, Iterable[str]],
                   vals: Iterable[Union[str, float]] = None) -> None:
        if isinstance(keys, dict):
            vals = keys.values()
            keys = keys.keys()
        vals = self.set_type(vals)
        self.rows.clear()
        for i, (key, val) in enumerate(zip(keys, vals)):
            self.rows.append({'id': i, 'key': key, 'val': val})
        self.update()

    def get_values(self, as_dict: bool = False) -> Union[Dict, Tuple[List, List]]:
        keys = [row.get('key') for row in self.rows]
        vals = self.set_type([row.get('val') for row in self.rows])
        if as_dict:
            return dict(zip(keys, vals))
        return keys, vals

    @staticmethod
    def set_type(vals):
        return vals


class UITable(Table):
    def __init__(self, columns: List[Dict] = None, rows: List[Dict] = None, row_key: str = 'id') -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key)
        self.add_slot('header', self.HEADER)
        self.add_slot('body', self.BODY)
        self.props('flat bordered separator=cell')

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
    BODY = f'''
        <q-tr :props="props">
            <q-td key="key" style="background-color:#212121" :props="props">
                <q-input v-model="props.row.key" dense borderless debounce="{CONFIG.debounce}"
                @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
            </q-td>
            <q-td key="val" style="background-color:#263238" :props="props">
                <q-input v-model="props.row.val" dense borderless debounce="{CONFIG.debounce}"
                @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
            </q-td>
            <q-td auto-width style="background-color:#006064">
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


class UIGrid(Table):
    def __init__(self, columns: List[Dict] = None, rows: List[Dict] = None,
                 row_key: str = 'id', item_size: int = 100) -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key)
        self.item_size = item_size
        self.add_slot('item', self._item())
        self.props('hide-header grid')

    def _item(self) -> str:
        # TODO: custom size/width for each input element pair
        return f'''
            <div class="column" style="width:{self.item_size}px; height:70px" :props="props">
                <div class="col">
                    <q-input v-model="props.row.key" dense outlined debounce="{CONFIG.debounce}" bg-color=grey-10
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </div>
                <div class="col-xl-7">
                    <q-input v-model="props.row.val" dense outlined debounce="{CONFIG.debounce}" bg-color=blue-grey-10
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </div>
            </div>
        '''


class UIList(Table):
    def __init__(self, columns: List[Dict] = None, rows: List[Dict] = None,
                 row_key: str = 'id', val_type: str = 'text') -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key)
        self.val_type = val_type
        self.add_slot('body', self._body())
        self.props('hide-header separator=none')
        self.style('min-width:400px')

    def set_type(self, vals):
        if self.val_type == 'number':
            return list(map(float, vals))
        return vals

    def _body(self) -> str:
        return f'''
            <q-tr :props="props">
                <q-td key="key" :props="props">
                    {{{{ props.row.key }}}}
                    <q-input v-model="props.row.val" type="{self.val_type}" dense outlined debounce="{CONFIG.debounce}"
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </q-td>
            </q-tr>
        '''
