from nicegui import ui, events
from backend.config.const import CONFIG, URLS
from backend.config.const import PUNCTUATIONS, BEG_PATTERNS, END_PATTERNS, QUO_PATTERNS, REPLACEMENTS
from backend.dicts.dictonaries import Dicts
from frontend.pages.ui_custom import ui_dialog, TABLE, LIST
from frontend.pages.page_abc import Page


class Settings(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.SETTINGS)
        self.dicts: Dicts = Dicts()
        self.ui_list: ui.table = None  # noqa
        self.ui_table: ui.table = None  # noqa
        self.ui_punctuations: ui.input = None  # noqa
        self.ui_beg_patterns: ui.input = None  # noqa
        self.ui_end_patterns: ui.input = None  # noqa
        self.ui_quo_patterns: ui.input = None  # noqa

    def _open_previous_url(self) -> None:
        self._update_replacements()
        self._update_patterns()
        # do not update url history in settings
        ui.open(f'{self.url_history[0]}')

    def _reset_interface(self) -> None:
        pass

    def _update_interface(self) -> None:
        pass

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

    def _upd_param(self, event: events.GenericEventArguments) -> None:
        for row in self.ui_list.rows:
            if row.get('id') == event.args.get('id'):
                row.update(event.args)

    def _load_list(self) -> None:
        self.ui_list.rows.clear()
        keys = [
            'Tab size',
            'Use page seperator [0, 1]',
            'Characters per line',
            'Lines per page',
            'Title font size',
            'Font size',
            'PDF width',
            'PDF block height'
        ]
        for i, (key, val) in enumerate(zip(keys, self.pdf.values())):
            self.ui_list.rows.append({'id': i, 'key': key, 'val': float(val)})
        self.ui_list.update()

    def _reset_list(self) -> None:
        self.pdf = CONFIG.PDF
        self._load_list()

    def _update_pdf_params(self):
        vals = [row.get('val') for row in self.ui_list.rows]
        for key, val in zip(self.pdf.keys(), vals):
            if key == 'page_sep':
                self.pdf[key] = bool(val)
            elif key in ['word_space', 'char_lim', 'line_lim']:
                self.pdf[key] = int(val)
            else:
                self.pdf[key] = float(val)

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

    @staticmethod
    def _dialog_interface() -> ui_dialog:
        label_list = [
            'Some tips for the user interface!'
        ]
        return ui_dialog(label_list = label_list)

    @staticmethod
    def _dialog_replacements() -> ui_dialog:
        label_list = [
            'Some tips for the user interface!'
        ]
        return ui_dialog(label_list = label_list)

    @staticmethod
    def _dialog_pdf_settings() -> ui_dialog:
        label_list = [
            'Some tips for the user interface!'
        ]
        return ui_dialog(label_list = label_list)

    @staticmethod
    def _dialog_adv_settings() -> ui_dialog:
        label_list = [
            'Some tips for the user interface!'
        ]
        return ui_dialog(label_list = label_list)

    def _header(self) -> None:
        with ui.header():
            ui.button(text = 'GO BACK', on_click = self._open_previous_url)
            ui.label('SETTINGS').classes('absolute-center')

    def _center(self) -> None:
        self.dicts.load(uuid = self.decoder.uuid)

        with ui.column().classes('w-full items-center').style('font-size:12pt'):
            with ui.tabs() as tabs:
                panel0 = ui.tab('INTERFACE SETTINGS')
                panel1 = ui.tab('REPLACEMENTS')
                panel2 = ui.tab('PDF SETTINGS')
                panel3 = ui.tab('ADVANCED SETTINGS')
            with ui.tab_panels(tabs, value = panel0, animated = True):
                with ui.tab_panel(panel0).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_interface().open) \
                            .classes('absolute-top-right'):
                        ui.tooltip('Need help?')
                    self._interface()
                with ui.tab_panel(panel1).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_replacements().open) \
                            .classes('absolute-top-right'):
                        ui.tooltip('Need help?')
                    self._table()
                    self._load_table()
                with ui.tab_panel(panel2).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_pdf_settings().open) \
                            .classes('absolute-top-right'):
                        ui.tooltip('Need help?')
                    self._pdf_settings()
                    self._load_list()
                with ui.tab_panel(panel3).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_adv_settings().open) \
                            .classes('absolute-top-right'):
                        ui.tooltip('Need help?')
                    self._adv_settings()

    def _interface(self) -> None:
        # TODO: finish tab for interface settings
        ui.checkbox('Show tooltips')
        ui.separator()
        with ui.button(icon = 'save', on_click = self._update_interface):
            ui.tooltip('Save settings')
        with ui.button(icon = 'restore', on_click = self._reset_interface) \
                .classes('absolute-bottom-left'):
            ui.tooltip('Reset settings')

    def _table(self) -> None:
        columns = [
            {'label': 'Character ', 'name': 'key', 'field': 'key', 'required': True, 'sortable': True, 'align': 'left'},
            {'label': 'Substitute', 'name': 'val', 'field': 'val', 'required': True, 'sortable': True, 'align': 'left'},
        ]
        self.ui_table = ui.table(columns = columns, rows = [], row_key = 'id') \
            .props('flat bordered separator=cell') \
            .style('min-width:450px; max-height:80vh;')
        self.ui_table.add_slot('header', TABLE.HEADER)
        self.ui_table.add_slot('body', TABLE.BODY)
        self.ui_table.on('_upd_row', self._upd_row)
        self.ui_table.on('_del_row', self._del_row)
        self.ui_table.on('_add_row', self._add_row)
        ui.separator()
        with ui.row():
            with ui.button(icon = 'save', on_click = self._update_replacements):
                ui.tooltip('Save settings')
            with ui.button(icon = 'restore', on_click = self._reset_table) \
                    .classes('absolute-bottom-left'):
                ui.tooltip('Reset settings')
            with ui.button(icon = 'delete', on_click = self._clear_table) \
                    .classes('absolute-bottom-right'):
                ui.tooltip('Clear settings')

    def _pdf_settings(self) -> None:
        columns = [
            {'name': 'key', 'field': 'key', 'required': True, 'align': 'left'},
            {'name': 'val', 'field': 'val', 'required': True, 'align': 'left'},
        ]
        self.ui_list = ui.table(columns = columns, rows = [], row_key = 'id') \
            .props('hide-header separator=none') \
            .style('min-width:250px')
        self.ui_list.add_slot('body', LIST.BODY)
        self.ui_list.on('_upd_param', self._upd_param)
        ui.separator()
        with ui.button(icon = 'save', on_click = None):
            ui.tooltip('Save settings')
        with ui.button(icon = 'restore', on_click = None) \
                .classes('absolute-bottom-left'):
            ui.tooltip('Reset settings')

    def _adv_settings(self) -> None:
        with ui.card().style('gap: 0.0rem; font-size:10pt'):
            ui.label('Punctuations')
            self.ui_punctuations = ui.input(value = self.decoder.punctuations) \
                .style('font-size:12pt')
            ui.space().style('height:15px')
            ui.label('Beginning Patterns')
            self.ui_beg_patterns = ui.input(value = self.decoder.beg_patterns) \
                .style('font-size:12pt')
            ui.space().style('height:15px')
            ui.label('End Pattern')
            self.ui_end_patterns = ui.input(value = self.decoder.end_patterns) \
                .style('font-size:12pt')
            ui.space().style('height:15px')
            ui.label('Quotations')
            self.ui_quo_patterns = ui.input(value = self.decoder.quo_patterns) \
                .style('font-size:12pt')
        ui.separator()
        with ui.button(icon = 'save', on_click = self._update_patterns):
            ui.tooltip('Save settings')
        with ui.button(icon = 'restore', on_click = self._reset_patterns) \
                .classes('absolute-bottom-left'):
            ui.tooltip('Reset settings')

    def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
