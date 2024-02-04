from nicegui import ui, events
from backend.config.const import URLS
from backend.config.const import PUNCTUATIONS, BEG_PATTERNS, END_PATTERNS, QUO_PATTERNS, REPLACEMENTS
from backend.dicts.dictonaries import Dicts
from frontend.pages.ui_config import TABLE
from frontend.pages.page_abc import Page


class Settings(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.SETTINGS)
        self.dicts: Dicts = Dicts()
        self.ui_table: ui.table = None
        self.ui_punctuations: ui.input = None
        self.ui_beg_patterns: ui.input = None
        self.ui_end_patterns: ui.input = None
        self.ui_quo_patterns: ui.input = None

    def _open_previous_url(self) -> None:
        self._update_replacements()
        self._update_patterns()
        # do not update url history in settings
        ui.open(f'{self.url_history[0]}')

    def _add_row(self, event: events.GenericEventArguments) -> None:
        _id = max(row.get('id') for row in self.ui_table.rows) + 1
        if event.args:
            for i, row in enumerate(self.ui_table.rows):
                if row.get('id') == event.args.get('id'):
                    self.ui_table.rows.insert(i + 1, {'id': _id, 'key': '', 'val': ''})
        else:
            self.ui_table.rows.insert(0, {'id': _id, 'key': '', 'val': ''})
        self.ui_table.update()

    def _del_row(self, event: events.GenericEventArguments) -> None:
        self.ui_table.rows[:] = [row for row in self.ui_table.rows if row.get('id') != event.args.get('id')]
        self.ui_table.update()

    def _upd_row(self, event: events.GenericEventArguments) -> None:
        for row in self.ui_table.rows:
            if row.get('id') == event.args.get('id'):
                row.update(event.args)

    def _clear_table(self) -> None:
        self.dicts.replacements.clear()
        self.ui_table.rows.clear()
        self.ui_table.update()

    def _load_table(self) -> None:
        self.ui_table.rows.clear()
        for i, (key, val) in enumerate(self.dicts.replacements.items()):
            self.ui_table.rows.insert(0, {'id': i, 'key': key, 'val': val})
        self.ui_table.update()

    def _reset_table(self) -> None:
        self.dicts.replacements = REPLACEMENTS
        self._load_table()

    def _update_replacements(self) -> None:
        keys = [row.get('key') for row in self.ui_table.rows]
        vals = [row.get('val') for row in self.ui_table.rows]
        self.dicts.replacements = dict(zip(keys, vals))
        self.dicts.save(uuid = self.decoder.uuid)

    def _reset_patterns(self) -> None:
        self.ui_punctuations.value = PUNCTUATIONS
        self.ui_beg_patterns.value = BEG_PATTERNS
        self.ui_end_patterns.value = END_PATTERNS
        self.ui_quo_patterns.value = QUO_PATTERNS
        self.decoder.punctuations = PUNCTUATIONS
        self._update_patterns()

    def _update_patterns(self) -> None:
        self.decoder.punctuations = self.ui_punctuations.value
        self.decoder.beg_patterns = self.ui_beg_patterns.value
        self.decoder.end_patterns = self.ui_end_patterns.value
        self.decoder.quo_patterns = self.ui_quo_patterns.value

    def _header(self) -> None:
        with ui.header().style('align-items: center'):
            ui.button(text = 'GO BACK', on_click = self._open_previous_url)
            ui.label('SETTINGS').classes('absolute-center')

    def _center(self) -> None:
        self.dicts.load(uuid = self.decoder.uuid)

        with ui.column().classes(f'{self.abs_top_center(50)} w-[80%]').style(
                'align-items: center; font-size: 12pt'):
            with ui.tabs() as tabs:
                panel0 = ui.tab('PDF SETTINGS')
                panel1 = ui.tab('REPLACEMENTS')
                panel2 = ui.tab('ADVANCED SETTINGS')
            with ui.tab_panels(tabs, value = panel0, animated = True):
                with ui.tab_panel(panel0).style('align-items: center; min-width: 600px'):
                    self._pdf_settings()
                    ui.button(icon = 'help', on_click = None).classes('absolute-top-right')
                with ui.tab_panel(panel1).classes('w-fit').style('align-items: center; min-width: 600px'):
                    self._table()
                    self._load_table()
                    ui.button(icon = 'help', on_click = None).classes('absolute-top-right')
                with ui.tab_panel(panel2).style('align-items: center; min-width: 600px'):
                    self._adv_settings()
                    ui.button(icon = 'help', on_click = None).classes('absolute-top-right')
            self.ui_space(height = 100)

    def _pdf_settings(self):
        # TODO: finish tab for pdf settings
        ui.input(label = '', value = '') \
            .style('font-size: 12pt')
        ui.input(label = '', value = '') \
            .style('font-size: 12pt')
        ui.input(label = '', value = '') \
            .style('font-size: 12pt')
        ui.input(label = '', value = '') \
            .style('font-size: 12pt')
        ui.input(label = '', value = '') \
            .style('font-size: 12pt')
        ui.input(label = '', value = '') \
            .style('font-size: 12pt')
        ui.input(label = '', value = '') \
            .style('font-size: 12pt')
        ui.input(label = '', value = '') \
            .style('font-size: 12pt')
        ui.separator()
        ui.button(icon = 'save', on_click = None)
        ui.button(icon = 'restore', on_click = None).classes('absolute-bottom-left')

    def _table(self) -> None:
        # TODO: prevent double key usage (maybe also pop-out editing to normal input)
        # TODO: table coloring
        columns = [
            {'label': 'Character ', 'name': 'key', 'field': 'key', 'required': True, 'sortable': True, 'align': 'left'},
            {'label': 'Substitute', 'name': 'val', 'field': 'val', 'required': True, 'sortable': True, 'align': 'left'},
        ]
        self.ui_table = ui.table(columns = columns, rows = [], row_key = 'key') \
            .classes('header-color') \
            .props('flat bordered separator=cell') \
            .style('min-width:450px; max-height:80vh;')
        self.ui_table.add_slot('header', TABLE.HEADER)
        self.ui_table.add_slot('body', TABLE.BODY)
        self.ui_table.on('_upd_row', self._upd_row)
        self.ui_table.on('_del_row', self._del_row)
        self.ui_table.on('_add_row', self._add_row)
        ui.separator()
        with ui.row():
            ui.button(icon = 'restore', on_click = self._reset_table).classes('absolute-bottom-left')
            ui.button(icon = 'save', on_click = self._update_replacements)
            ui.button(icon = 'delete', on_click = self._clear_table).classes('absolute-bottom-right')

    def _adv_settings(self) -> None:
        self.ui_punctuations = ui.input(label = 'Punctuations', value = self.decoder.punctuations) \
            .style('font-size: 12pt')
        self.ui_beg_patterns = ui.input(label = 'Beginning Patterns', value = self.decoder.beg_patterns) \
            .style('font-size: 12pt')
        self.ui_end_patterns = ui.input(label = 'End Pattern', value = self.decoder.end_patterns) \
            .style('font-size: 12pt')
        self.ui_quo_patterns = ui.input(label = 'Quotations', value = self.decoder.quo_patterns) \
            .style('font-size: 12pt')
        ui.separator()
        ui.button(icon = 'save', on_click = self._update_patterns)
        ui.button(icon = 'restore', on_click = self._reset_patterns).classes('absolute-bottom-left')

    def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
