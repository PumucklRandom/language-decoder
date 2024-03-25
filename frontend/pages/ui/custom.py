from typing import Union, Tuple, Dict, List, Iterable
from nicegui import ui, events
from backend.config.config import CONFIG
from backend.utils.utilities import lonlen
from frontend.pages.ui.config import COLORS, DEFAULT_COLS, SIZE_FACTOR


# .style('min-width:500px; max-height:80vh', 'min-width:500px;)
def ui_dialog(label_list: List[str], space: int = 10) -> ui.dialog:
    with ui.dialog() as dialog:
        with ui.card().classes('min-w-[80%]').style('width:200px; min-height:112px; gap:0.0rem'):
            ui.button(icon = 'close', on_click = dialog.close) \
                .classes('absolute-top-right') \
                .props('dense round size=12px')
            ui.space().style(f'height:{space}px')
            for label in label_list:
                if label == '\n':
                    ui.space().style(f'height:{space}px')
                elif label == '/n':
                    ui.separator().style(f'height:{2}px')
                else:
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
        if not event.args:
            self.rows.insert(0, {'id': _id, 'key': '', 'val': ''})
            self.update()
            return
        for i, row in enumerate(self.rows):
            if row.get('id') == event.args.get('id'):
                self.rows.insert(i + 1, {'id': _id, 'key': '', 'val': ''})
        self.update()

    def _del_row(self, event: events.GenericEventArguments) -> None:
        self.rows[:] = [row for row in self.rows if row.get('id') != event.args.get('id')]
        self.update()

    def _upd_row(self, event: events.GenericEventArguments) -> None:
        for row in self.rows:
            if row.get('id') == event.args.get('id'):
                row.update(event.args)

    def _set_type(self, vals) -> List[Union[str, float]]:
        return vals

    def set_values(self, keys: Union[Dict, Iterable[str]],
                   vals: Iterable[Union[str, float]] = None) -> None:
        if isinstance(keys, dict):
            vals = keys.values()
            keys = keys.keys()
        vals = self._set_type(vals)
        self.rows.clear()
        for i, (key, val) in enumerate(zip(keys, vals)):
            self.rows.append({'id': i, 'key': key, 'val': val})
        self.update()

    def get_values(self, as_dict: bool = False) -> Union[Dict, Tuple[List, List]]:
        keys = [row.get('key') for row in self.rows]
        vals = self._set_type([row.get('val') for row in self.rows])
        if as_dict:
            return dict(zip(keys, vals))
        return keys, vals


class UITable(Table):
    def __init__(self, columns: List[Dict] = None, rows: List[Dict] = None,
                 row_key: str = 'id', dark_mode: bool = True) -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key)
        if dark_mode:
            self.key_color = COLORS.GREY_10.VAL
            self.val_color = COLORS.BLUE_GREY_10.VAL
            self.btn_color = COLORS.CYAN_10.VAL
        else:
            self.key_color = COLORS.GREY_1.VAL
            self.val_color = COLORS.BLUE_GREY_1.VAL
            self.btn_color = COLORS.CYAN_1.VAL
        self.add_slot('header', self._header)
        self.add_slot('body', self._body())
        self.props('flat bordered separator=cell')

    _header = f'''
        <q-tr style="background-color:{COLORS.PRIMARY.VAL}" :props="props">
            <q-th v-for="col in props.cols" :key="col.field" :props="props">
                {{{{ col.label }}}}
            </q-th>
            <q-th auto-width>
                <q-btn icon="add" size="12px" dense round color="{COLORS.PRIMARY.KEY}" :props="props"
                @click="() => $parent.$emit('_add_row')"/>
                <!-- <q-tooltip> add row below </q-tooltip> -->
            </q-th>
        </q-tr>
    '''

    def _body(self) -> str:
        return f'''
        <q-tr :props="props">
            <q-td key="key" style="background-color:{self.key_color}" :props="props">
                <q-input v-model="props.row.key" dense borderless debounce="{CONFIG.debounce}"
                @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
            </q-td>
            <q-td key="val" style="background-color:{self.val_color}" :props="props">
                <q-input v-model="props.row.val" dense borderless debounce="{CONFIG.debounce}"
                @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
            </q-td>
            <q-td auto-width style="background-color:{self.btn_color}">
                <div class="col">
                    <q-btn icon="remove" size="8px" dense round color="{COLORS.PRIMARY.KEY}"
                    @click="() => $parent.$emit('_del_row', props.row)" :props="props"/>
                    <!-- <q-tooltip> delete row </q-tooltip> -->
                </div>
                <div class="col">
                    <q-btn icon="add" size="8px" dense round color="{COLORS.PRIMARY.KEY}"
                    @click="() => $parent.$emit('_add_row', props.row)" :props="props"/>
                    <!-- <q-tooltip> add row below </q-tooltip> -->
                </div>
            </q-td>
        </q-tr>
    '''


class UIGrid(Table):
    def __init__(self, columns: List[Dict] = None, rows: List[Dict] = None, row_key: str = 'id',
                 source_words: List[str] = None, target_words: List[str] = None,
                 preload: bool = False, dark_mode: bool = True) -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key)
        self.item_size = 100
        if preload:
            target_words = [''] * len(source_words)
        if dark_mode:
            self.scr_color = COLORS.GREY_10.KEY
            self.tar_color = COLORS.BLUE_GREY_10.KEY
        else:
            self.scr_color = COLORS.GREY_1.KEY
            self.tar_color = COLORS.BLUE_GREY_1.KEY
        self._set_item_size(words = source_words + target_words)
        self.add_slot('item', self._item())
        self.props('hide-header grid')
        self.set_values(source_words, target_words)

    def _set_item_size(self, words: List[str] = None) -> None:
        if words and isinstance(words, list):
            chars = lonlen(words)
            chars = 20 if chars > 20 else chars
            self.item_size = chars * SIZE_FACTOR

    def _item(self) -> str:
        # TODO: custom size/width for each input element pair
        return f'''
            <div class="column" style="width:{self.item_size}px; height:70px" :props="props">
                <div class="col">
                    <q-input v-model="props.row.key" dense outlined 
                    debounce="{CONFIG.debounce}" bg-color={self.scr_color}
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </div>
                <div class="col-xl-7">
                    <q-input v-model="props.row.val" dense outlined
                    debounce="{CONFIG.debounce}" bg-color={self.tar_color}
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

    def _set_type(self, vals) -> List[float]:
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
