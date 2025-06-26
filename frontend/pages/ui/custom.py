import re
from re import Pattern
from typing import Union, Iterable
from nicegui import ui, events
from backend.config.config import CONFIG
from backend.utils.utilities import maxlen
from frontend.pages.ui.config import DEFAULT_COLS, COLORS, JS, top_left, bot_right


def ui_dialog(label_list: list[str], width: int = 800, u_width: str = 'px',
              height: int = 100, max_width: int = 80, space: int = 10) -> ui.dialog:
    """
    :param label_list: list of labels to display in the dialog
    :param width: width of the dialog in pixels
    :param u_width: unit for the width of the dialog, e.g. 'px' or 'vw'
    :param height: height of the dialog in pixels
    :param max_width: maximum width of the dialog in percent
    :param space: height space between the labels in pixels
    """
    with ui.dialog() as dialog:
        with ui.card().classes(f'max-w-[{max_width}%]') \
                .style(f'min-width:{width}{u_width}; min-height:{height}px; font-size:12pt; gap:0.0rem'):
            ui.button(icon = 'close', on_click = dialog.close) \
                .classes('absolute-top-right') \
                .props('dense round size=12px')
            ui.space().style(f'height:{space}px')
            for label in label_list:
                if label == '/n':
                    ui.space().style(f'height:{space}px')
                elif label == '/N':
                    ui.separator().style(f'height:{2}px')
                else:
                    ui.label(label)
    return dialog


class UIUpload(object):
    __slots__ = ('_upload',)

    def __init__(self, text: str = '', *args, **kwargs) -> None:
        with ui.element().classes('relative'):
            self._upload = ui.upload(*args, **kwargs).style('width: 340px; font-size:12pt').props('flat')
            ui.button(
                text = text,
                on_click = lambda: self._upload.run_method('pickFiles')) \
                .classes(top_left(25, 170, center = True)) \
                .style('font-size:11pt; width:324px') \
                .props('dense')

    def classes(self, css: str) -> None:
        self._upload.classes(css)

    def style(self, style: str) -> None:
        self._upload.style(style)

    def props(self, props: str) -> None:
        self._upload.props(props)


class Table(ui.table):
    __slots__ = ()

    def __init__(self, columns: list[dict] = None, rows: list[dict] = None,
                 row_key: str = 'id', *args, **kwargs) -> None:
        if columns is None: columns = DEFAULT_COLS
        if rows is None: rows = []
        super().__init__(columns = columns, rows = rows, row_key = row_key, *args, **kwargs)
        self.on('_upd_row', self._upd_row)
        self.on('_del_row', self._del_row)
        self.on('_add_row', self._add_row)

    def _add_row(self, event: events.GenericEventArguments) -> None:
        _id = max((row.get('id', -1) for row in self.rows), default = -1) + 1
        if not event.args:
            self.rows.insert(0, {'id': _id, 'source': '', 'target': ''})
            self.update()
            return
        row_id = event.args.get('id')
        for i, row in enumerate(self.rows):
            if row.get('id') == row_id:
                self.rows.insert(i + 1, {'id': _id, 'source': '', 'target': ''})
                break
        self.update()

    def _del_row(self, event: events.GenericEventArguments) -> None:
        row_id = event.args.get('id')
        self.rows.pop(next(i for i, row in enumerate(self.rows) if row.get('id') == row_id))
        self.update()

    def _upd_row(self, event: events.GenericEventArguments) -> None:
        row_id = event.args.get('id')
        for row in self.rows:
            if row.get('id') == row_id:
                row.update(event.args)
                break

    def _set_type(self, values) -> list[Union[str, float]]:
        return values

    def set_values(self, sources: Union[dict, Iterable[str]],
                   targets: Iterable[Union[str, float]] = None) -> None:
        if isinstance(sources, dict):
            targets = sources.values()
            sources = sources.keys()
        targets = self._set_type(targets)
        self.rows.clear()
        for i, (source, target) in enumerate(zip(sources, targets)):
            self.rows.append({'id': i, 'source': source, 'target': target})
        self.update()

    def get_values(self, as_dict: bool = False) -> Union[dict, tuple[list, list]]:
        sources = [f'{row.get("source")}'.strip() for row in self.rows]
        targets = self._set_type([f'{row.get("target")}'.strip() for row in self.rows])
        if as_dict:
            return dict(zip(sources, targets))
        return sources, targets


class UIList(Table):
    __slots__ = ('val_type',)

    def __init__(self, columns: list[dict] = None, rows: list[dict] = None,
                 row_key: str = 'id', val_type: str = 'text', *args, **kwargs) -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key, *args, **kwargs)
        self.val_type = val_type
        self.add_slot('body', self._body())
        self.style('min-width:420px')
        self.props('hide-header separator=none')

    def _set_type(self, values) -> list[float]:
        if self.val_type == 'number':
            return [float('nan') if val == '' else float(val) for val in values]
        return values

    # ; font-weight:bold
    def _body(self) -> str:
        return f'''
            <q-tr :props="props">
                <q-td key="source" style="font-size:16px" :props="props">
                    <div style="padding-left:5px">{{{{ props.row.source }}}}</div>
                    <q-input style="font-family:RobotoMono; font-size:11pt" v-model="props.row.target" 
                    type="{self.val_type}" dense outlined debounce="{CONFIG.debounce}"
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </q-td>
            </q-tr>
        '''


class UITable(Table):
    __slots__ = ('btn_color', 'scr_color', 'tar_color')

    def __init__(self, columns: list[dict] = None, rows: list[dict] = None, row_key: str = 'id',
                 dark_mode: bool = True, *args, **kwargs) -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key, *args, **kwargs)
        if dark_mode:
            self.btn_color = COLORS.PRIME_DARK.VAL
            self.scr_color = COLORS.GREY10.VAL
            self.tar_color = COLORS.BLUE_GREY10.VAL
        else:
            self.btn_color = COLORS.PRIME_LIGHT.VAL
            self.scr_color = COLORS.GREY1.VAL
            self.tar_color = COLORS.BLUE_GREY1.VAL
        self.add_slot('header', self._header)
        self.add_slot('body', self._body())
        self.classes('padding-bottom')
        self.props('flat bordered separator=cell')
        self.props['rows-per-page-options'] = CONFIG.table_options
        self.props['rows-per-page'] = CONFIG.table_options[2]

    _header = f'''
        <q-tr style="background-color:{COLORS.PRIMARY.VAL}" :props="props">
            <q-th v-for="col in props.cols" :key="col.field" :props="props"
                style="font-size:16px; text-align:center">
                {{{{ col.label }}}}
            </q-th>
            <q-th auto-width>
                <q-btn icon="add" size="14px" dense round color="{COLORS.PRIMARY.KEY}" :props="props"
                @click="() => $parent.$emit('_add_row')"/>
                <!-- <q-tooltip> add row below </q-tooltip> -->
            </q-th>

        </q-tr>
    '''

    def _body(self) -> str:
        return f'''
            <q-tr :props="props">
                <q-td key="source" style="background-color:{self.scr_color}" :props="props">
                    <q-input v-model="props.row.source" style="font-size: 11pt"
                        dense borderless debounce="{CONFIG.debounce}"
                        @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </q-td>
                <q-td key="target" style="background-color:{self.tar_color}" :props="props">
                    <q-input v-model="props.row.target" style="font-size: 11pt"
                        dense borderless debounce="{CONFIG.debounce}"
                        @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </q-td>
                <q-td auto-width style="background-color:{self.btn_color}; text-align:center">
                    <div style="position:absolute; top:50%; left:60%; transform:translate(-50%, -50%)">
                        <q-btn icon="delete" size="12px" dense round color="{COLORS.PRIMARY.KEY}"
                            @click="() => $parent.$emit('_del_row', props.row)" :props="props"/>
                        <!-- <q-tooltip> delete row </q-tooltip> -->
                    </div>
                    <div style="position:absolute; top:103%; left:-1%; transform:translate(-50%, -50%); z-index:1">
                        <q-btn icon="add" size="12px" dense round color="{COLORS.PRIMARY.KEY}"
                            @click="() => $parent.$emit('_add_row', props.row)" :props="props"/>
                        <!-- <q-tooltip> add row below </q-tooltip> -->
                    </div>
                </q-td>
            </q-tr>
        '''


class UIGrid(Table):
    __slots__ = ('scr_color', 'tar_color', 'item_size')

    def __init__(self, source_words: list[str] = None, target_words: list[str] = None,
                 columns: list[dict] = None, rows: list[dict] = None, row_key: str = 'id',
                 preload: bool = False, dark_mode: bool = True, *args, **kwargs) -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key, *args, **kwargs)
        if preload:
            target_words = [''] * len(source_words)
        if dark_mode:
            self.scr_color = COLORS.GREY10.KEY
            self.tar_color = COLORS.BLUE_GREY10.KEY
        else:
            self.scr_color = COLORS.GREY1.KEY
            self.tar_color = COLORS.BLUE_GREY1.KEY
        if source_words is None: source_words = []
        if target_words is None: target_words = []
        self.item_size = 100
        self._set_item_size(words = source_words + target_words)
        self.set_values(source_words, target_words)
        self.add_slot('item', self._item())
        self.props('hide-header grid')

    def _set_item_size(self, words: list[str] = None) -> None:
        if words and isinstance(words, list):
            chars = maxlen(words)
            self.item_size = int(CONFIG.size_bias + CONFIG.size_fct * chars)
            self.item_size = max(min(self.item_size, CONFIG.size_max), CONFIG.size_min)

    def _item(self) -> str:
        return f'''
            <div class="column" style="width:{self.item_size}px; height:70px" :props="props">
                <div class="col">
                    <q-input v-model="props.row.source" style="font-family:RobotoMono; font-size:11pt" 
                        debounce="{CONFIG.debounce}" bg-color={self.scr_color} dense outlined
                        @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </div>
                <div class="col-xl-7">
                    <q-input v-model="props.row.target" style="font-family:RobotoMono; font-size:11pt"
                        debounce="{CONFIG.debounce}" bg-color={self.tar_color} dense outlined
                        @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </div>
            </div>
        '''

    @staticmethod
    def mark_cells(find_str: str = '') -> None:
        if not find_str:
            ui.run_javascript(JS.CLEAR_CELLS)
            return
        ui.run_javascript(JS.mark_cells(find_str))


class UIGridPages(object):
    __slots__ = ('_page_number', '_page_size', '_prev_page', 'find_str', 'pattern',
                 'source_words', 'target_words', '_eos_indices', '_indices', '_s_indices',
                 '_ui_grid', '_ui_page', '_visible')

    def __init__(self, grid_page: dict = None, find_str: str = '',
                 endofs: str = CONFIG.Regex.endofs, quotes: str = CONFIG.Regex.quotes) -> None:
        self._page_number: int = 1
        self._page_size: int = CONFIG.grid_options[2]
        self._prev_page: int = 1
        self._set_grid_page(grid_page)
        self.find_str = find_str
        self.pattern: Pattern = re.compile(rf'.*?[{endofs}][{quotes}]?$')
        self.source_words: list[str] = []
        self.target_words: list[str] = []
        self._eos_indices: tuple[int] = ()  # end of sentence word indices
        self._indices: list[int] = []  # word indices per page
        self._s_indices: list[int] = []  # sentence indices per page
        self._ui_grid: UIGrid
        self._ui_page: ui.pagination
        self._visible: bool = False

    def page(self, *args, **kwargs) -> None:
        with ui.card().style('min-width:1000px; min-height:562px'):
            self._table(*args, **kwargs)
            ui.space().style('height:5px')

    def pagination(self):
        with ui.card().classes(bot_right(66, 0)).style('width:550px; height:50px') \
                .bind_visibility_from(self, '_visible'):
            ui.label('Max words per page:').classes(bot_right(15, 410)).style('font-size:10.5pt')
            ui.select(options = CONFIG.grid_options,
                      value = CONFIG.grid_options[2],
                      on_change = self._repage) \
                .classes(bot_right(5, 350)) \
                .style('width:50px; font-size:11pt') \
                .props('dense options-dense borderless popup-content-style="font-size: 10.5pt"') \
                .bind_value(self, '_page_size')
            self._ui_page = ui.pagination(
                min = 1, max = 1,
                direction_links = True,
                value = self._page_number,
                on_change = self._scroll) \
                .classes(bot_right(10, 0)) \
                .style('width:350px') \
                .props('max-pages="8"') \
                .bind_value(self, '_page_number')

    @ui.refreshable
    def _table(self, *args, **kwargs) -> None:
        if not self.source_words or not self._indices:
            self._visible = False
            self._ui_grid = UIGrid()
            return
        self._visible = True
        p = self._page_number - 1
        self._ui_grid = UIGrid(
            source_words = self.source_words[self._indices[p]:self._indices[p + 1]],
            target_words = self.target_words[self._indices[p]:self._indices[p + 1]],
            *args, **kwargs
        )
        self._ui_grid.mark_cells(self.find_str)

    def _get_indices(self, source_words: list[str]) -> None:
        self._eos_indices = tuple(i + 1 for i, word in enumerate(source_words) if self.pattern.match(word))

    def _set_indices(self) -> None:
        if not self._eos_indices: return
        self._indices, p, _i = [0], 0, 0
        if self._page_size != 'All':
            for i in self._eos_indices:
                if i > (self._indices[p] + self._page_size):
                    self._indices.append(_i)
                    p += 1
                _i = i
        if self._eos_indices[-1] != self._indices[-1]:
            self._indices.append(self._eos_indices[-1])
        self._ui_page.max = len(self._indices) - 1

    def _repage(self) -> None:
        # Here it is important that the page reset is done first, to trigger the right scrolling!
        if hasattr(self, '_ui_page'):
            self._ui_page.value = 1  # have to be first!!!
            self._prev_page = 1
            self._set_indices()
            self._set_s_indices()
            self._table.refresh()

    def _scroll(self) -> None:
        self._upd_values()
        self._prev_page = self._page_number
        self._table.refresh()

    def _upd_values(self):
        if self.source_words and self._indices:
            p = self._prev_page - 1
            (self.source_words[self._indices[p]:self._indices[p + 1]],
             self.target_words[self._indices[p]:self._indices[p + 1]]) = self._ui_grid.get_values()

    def _set_grid_page(self, grid_page: dict) -> None:
        if grid_page is None: grid_page = {}
        self._page_number = grid_page.get('page', 1)
        self._page_size = grid_page.get('rowsPerPage', CONFIG.grid_options[2])
        self._prev_page = self._page_number

    def get_grid_page(self) -> dict:
        return {'page': self._page_number, 'rowsPerPage': self._page_size}

    def set_values(self, source_words: list[str], target_words: list[str], preload: bool = False,
                   new_source: bool = False, new_indices: bool = False) -> None:
        if not source_words: return
        if new_source:
            self._ui_page.value = 1
            self._prev_page = 1
            self._get_indices(source_words)
            self._set_indices()
            self._set_s_indices()
        if new_indices:
            self._get_indices(source_words)
            self._set_indices()
            self._set_s_indices()
        self.source_words = source_words
        self.target_words = target_words
        self._table.refresh(preload = preload)

    def get_values(self) -> tuple[list[str], list[str]]:
        self._upd_values()
        return self.source_words, self.target_words

    def highlight_text(self, find_str: str = '') -> None:
        self.find_str = find_str
        self._ui_grid.mark_cells(self.find_str)

    def _set_s_indices(self):
        self._s_indices = [0]
        self._s_indices.extend((self._eos_indices.index(i) + 1) * 3 for i in self._indices[1:])

    @property
    def slice(self) -> slice:
        p = self._page_number - 1
        if not self._s_indices: return slice(None)
        return slice(self._s_indices[p], self._s_indices[p + 1] - 1)
