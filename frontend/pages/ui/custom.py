from typing import Union, Iterable
from nicegui import ui, events
from backend.config.config import CONFIG
from backend.utils.utilities import maxlen
from frontend.pages.ui.config import DEFAULT_COLS, COLORS, JS, bot_right


def ui_dialog(label_list: list[str], classes: str = 'max-w-[80%]',
              style: str = 'min-width:200px', space: int = 10) -> ui.dialog:
    with ui.dialog() as dialog:
        with ui.card().style(f'{style}; min-height:112px; font-size:11pt; gap:0.0rem').classes(f'{classes}'):
            ui.button(icon = 'close', on_click = dialog.close) \
                .props('dense round size=12px') \
                .classes('absolute-top-right')
            ui.space().style(f'height:{space}px')
            for label in label_list:
                if label == '/n':
                    ui.space().style(f'height:{space}px')
                elif label == '/N':
                    ui.separator().style(f'height:{2}px')
                else:
                    ui.label(label)
    return dialog


class Table(ui.table):

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
    def __init__(self, columns: list[dict] = None, rows: list[dict] = None,
                 row_key: str = 'id', val_type: str = 'text', *args, **kwargs) -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key, *args, **kwargs)
        self.val_type = val_type
        self.add_slot('body', self._body())
        self.props('hide-header separator=none')
        self.style('min-width:420px')

    def _set_type(self, values) -> list[float]:
        if self.val_type == 'number':
            return list(map(float, values))
        return values

    def _body(self) -> str:
        return f'''
            <q-tr :props="props">
                <q-td key="source" :props="props" style="font-size:14px; font-weight:bold">
                    <div style="padding-left:5px">{{{{ props.row.source }}}}</div>
                    <q-input style="font-family:RobotoMono" v-model="props.row.target" type="{self.val_type}"
                    dense outlined debounce="{CONFIG.debounce}"
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </q-td>
            </q-tr>
        '''


class UITable(Table):
    def __init__(self, columns: list[dict] = None, rows: list[dict] = None, row_key: str = 'id',
                 dark_mode: bool = True, *args, **kwargs) -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key, *args, **kwargs)
        if dark_mode:
            self.scr_color = COLORS.GREY10.VAL
            self.tar_color = COLORS.BLUE_GREY10.VAL
            self.btn_color = COLORS.CYAN10.VAL
        else:
            self.scr_color = COLORS.GREY1.VAL
            self.tar_color = COLORS.BLUE_GREY1.VAL
            self.btn_color = COLORS.CYAN1.VAL
        self.add_slot('header', self._header)
        self.add_slot('body', self._body())
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
                <q-btn icon="add" size="12px" dense round color="{COLORS.PRIMARY.KEY}" :props="props"
                @click="() => $parent.$emit('_add_row')"/>
                <!-- <q-tooltip> add row below </q-tooltip> -->
            </q-th>
        </q-tr>
    '''

    def _body(self) -> str:
        return f'''
            <q-tr :props="props">
                <q-td key="source" style="background-color:{self.scr_color}" :props="props">
                    <q-input v-model="props.row.source" dense borderless debounce="{CONFIG.debounce}"
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </q-td>
                <q-td key="target" style="background-color:{self.tar_color}" :props="props">
                    <q-input v-model="props.row.target" dense borderless debounce="{CONFIG.debounce}"
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
    def __init__(self, source_words: list[str] = None, target_words: list[str] = None,
                 columns: list[dict] = None, rows: list[dict] = None, row_key: str = 'id',
                 preload: bool = False, dark_mode: bool = True, *args, **kwargs) -> None:
        super().__init__(columns = columns, rows = rows, row_key = row_key, *args, **kwargs)
        if source_words is None: source_words = []
        if target_words is None: target_words = []
        self.item_size = 100
        if preload:
            target_words = [''] * len(source_words)
        if dark_mode:
            self.scr_color = COLORS.GREY4.VAL
            self.scr_bg_color = COLORS.GREY10.KEY
            self.tar_color = COLORS.GREY1.VAL
            self.tar_bg_color = COLORS.BLUE_GREY10.KEY
        else:
            self.scr_color = COLORS.GREY10.VAL
            self.scr_bg_color = COLORS.GREY1.KEY
            self.tar_color = COLORS.DARK_PAGE.VAL
            self.tar_bg_color = COLORS.BLUE_GREY1.KEY
        self._set_item_size(words = source_words + target_words)
        self.add_slot('item', self._item())
        self.props('hide-header grid')
        self.set_values(source_words, target_words)

    def _set_item_size(self, words: list[str] = None) -> None:
        if words and isinstance(words, list):
            chars = maxlen(words)
            self.item_size = int(chars * CONFIG.size_fct + 3 * CONFIG.size_fct)
            self.item_size = max(min(self.item_size, CONFIG.size_max), CONFIG.size_min)

    def _item(self) -> str:
        return f'''
            <div class="column" style="width:{self.item_size}px; height:70px" :props="props">
                <div class="col">
                    <q-input style="font-family:RobotoMono" input-style="color:{self.scr_color}"
                    v-model="props.row.source" debounce="{CONFIG.debounce}" bg-color={self.scr_bg_color}
                    dense outlined @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </div>
                <div class="col-xl-7">
                    <q-input style="font-family:RobotoMono" input-style="color:{self.tar_color}"
                    v-model="props.row.target"  debounce="{CONFIG.debounce}" bg-color={self.tar_bg_color}
                    dense outlined @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
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
    def __init__(self, grid_page: dict = None, endofs: str = '.!?\'"', find_str: str = '') -> None:
        self.page_number: int = 1
        self.page_size: int = CONFIG.grid_options[2]
        self.prev_page: int = 1
        self.set_grid_page(grid_page)
        self.endofs = tuple(endofs)
        self.find_str: str = find_str
        self.source_words: list = []
        self.target_words: list = []
        self.eos_indices = []
        self.indices = []
        self.ui_grid: UIGrid
        self.ui_page: ui.pagination
        self.visible: bool = False

    def __call__(self, *args, **kwargs) -> None:
        with ui.card().style('min-width:1000px; min-height:562px'):
            self._table(*args, **kwargs)
            ui.space().style('height:5px')
            with ui.element().bind_visibility_from(self, 'visible'):
                ui.label('Max words per page:').classes(bot_right(15, 410))
                ui.select(options = CONFIG.grid_options,
                          value = CONFIG.grid_options[2],
                          on_change = self.repage) \
                    .props('dense options-dense borderless') \
                    .style('width:50px') \
                    .classes(bot_right(5, 350)) \
                    .bind_value(self, 'page_size')
                self.ui_page = ui.pagination(
                    min = 1, max = 1,
                    direction_links = True,
                    value = self.page_number,
                    on_change = self.scroll) \
                    .props('max-pages="8"') \
                    .style('width:350px') \
                    .classes(bot_right(10, 0)) \
                    .bind_value(self, 'page_number')

    @ui.refreshable
    def _table(self, *args, **kwargs) -> None:
        if not self.source_words or not self.indices:
            self.visible = False
            with ui.element().style('height:500px'):
                self.ui_grid = UIGrid()
            return
        self.visible = True
        p = self.page_number - 1
        self.ui_grid = UIGrid(
            source_words = self.source_words[self.indices[p]:self.indices[p + 1]],
            target_words = self.target_words[self.indices[p]:self.indices[p + 1]],
            *args, **kwargs
        )
        self.ui_grid.mark_cells(self.find_str)

    def get_indices(self, source_words: list[str]) -> None:
        self.eos_indices = [i + 1 for i, word in enumerate(source_words) if word.endswith(self.endofs)]

    def set_indices(self) -> None:
        if not self.eos_indices: return
        self.indices, p, _i = [0], 0, 0
        if self.page_size != 'All':
            for i in self.eos_indices:
                if i > (self.indices[p] + self.page_size):
                    self.indices.append(_i)
                    p += 1
                _i = i
        if self.eos_indices[-1] != self.indices[-1]:
            self.indices.append(self.eos_indices[-1])
        self.ui_page.max = len(self.indices) - 1

    def repage(self) -> None:
        if not hasattr(self, 'ui_page'): return
        # Here it is important that the page reset is done first, to trigger the right scrolling!
        self.ui_page.value = 1  # have to be first!!!
        self.prev_page = 1
        self.set_indices()
        self._table.refresh()

    def scroll(self) -> None:
        self.upd_values()
        self.prev_page = self.page_number
        self._table.refresh()

    def upd_values(self):
        if self.source_words and self.indices:
            p = self.prev_page - 1
            (self.source_words[self.indices[p]:self.indices[p + 1]],
             self.target_words[self.indices[p]:self.indices[p + 1]]) = self.ui_grid.get_values()

    def set_values(self, source_words: list[str], target_words: list[str], preload: bool = False,
                   new_source: bool = False, new_indices: bool = False) -> None:
        if not source_words: return
        if new_source:
            self.ui_page.value = 1
            self.prev_page = 1
            self.get_indices(source_words)
            self.set_indices()
        if new_indices:
            self.get_indices(source_words)
            self.set_indices()
        self.source_words = source_words
        self.target_words = target_words
        self._table.refresh(preload = preload)

    def get_values(self) -> tuple[list[str], list[str]]:
        self.upd_values()
        return self.source_words, self.target_words

    def get_grid_page(self) -> dict:
        return {'page': self.page_number, 'rowsPerPage': self.page_size}

    def set_grid_page(self, grid_page: dict) -> None:
        if grid_page is None: grid_page = {}
        self.page_number = grid_page.get('page', 1)
        self.page_size = grid_page.get('rowsPerPage', CONFIG.grid_options[2])
        self.prev_page = self.page_number

    def highlight_text(self, find_str: str = '') -> None:
        self.find_str = find_str
        self.ui_grid.mark_cells(self.find_str)
