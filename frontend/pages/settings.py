from nicegui import ui, events

from backend.config.const import CONFIG, URLS, REPLACE_COLS, PDF_COLS
from backend.config.const import PUNCTUATIONS, BEG_PATTERNS, END_PATTERNS, QUO_PATTERNS, REPLACEMENTS
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.dicts.dictonaries import Dicts
from frontend.pages.ui_custom import ui_dialog, TABLE, LIST, load_language, get_languages
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
        self._update_pdf_params()
        self._update_patterns()
        # do not update url history in settings
        ui.open(f'{self.url_history[0]}')

    def _refresh_interface(self) -> None:
        self.decoder.proxies = self.settings.get_proxies()
        ui.open(f'{self.URL}')

    def _reset_interface(self) -> None:
        self.settings.dark_mode = True
        self.settings.show_tips = True
        self.settings.language = 'english'
        self.settings.proxy_http = ''
        self.settings.proxy_https = ''

    def _connection_check(self):
        try:
            self.decoder.translate_source(source = 'test')
            ui.notify(self.ui_language.SETTINGS.Messages.connect_check[0],
                      type = 'positive', position = 'top')
        except DecoderError as exception:
            ui.notify(exception.message,
                      type = 'warning', position = 'top')
        except Exception as exception:
            message = 'Connection failed!'
            logger.error(f'{message} with exception:\n{exception}')
            ui.notify(self.ui_language.SETTINGS.Messages.connect_check[1],
                      type = 'warning', position = 'top')

    def _on_select(self) -> None:
        self.ui_language = load_language(language = self._language)

    def _add_row(self, event: events.GenericEventArguments) -> None:
        _id = max([row.get('id') for row in self.ui_table.rows] + [-1]) + 1
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
            self.ui_table.rows.append({'id': i, 'key': key, 'val': val})
        self.ui_table.update()

    def _reset_table(self) -> None:
        self.dicts.replacements = REPLACEMENTS.copy()
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
        for i, (key, val) in enumerate(zip(self.ui_language.SETTINGS.Pdf, self.pdf_params.values())):
            self.ui_list.rows.append({'id': i, 'key': key, 'val': float(val)})
        self.ui_list.update()

    def _reset_list(self) -> None:
        self.pdf_params = CONFIG.pdf.__dict__.copy()
        self._load_list()

    def _update_pdf_params(self):
        vals = [row.get('val') for row in self.ui_list.rows]
        for key, val in zip(self.pdf_params.keys(), vals):
            if key == 'page_sep':
                if val: self.pdf_params[key] = bool(val)
            elif key in ['tab_size', 'char_lim', 'line_lim']:
                if val: self.pdf_params[key] = int(val)
            else:
                if val: self.pdf_params[key] = float(val)

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

    def _dialog_interface(self) -> ui_dialog:
        return ui_dialog(label_list = self.ui_language.SETTINGS.Dialogs_interface)

    def _dialog_replacements(self) -> ui_dialog:

        return ui_dialog(label_list = self.ui_language.SETTINGS.Dialogs_replace)

    def _dialog_pdf_settings(self) -> ui_dialog:

        return ui_dialog(label_list = self.ui_language.SETTINGS.Dialogs_adv)

    def _dialog_adv_settings(self) -> ui_dialog:

        return ui_dialog(label_list = self.ui_language.SETTINGS.Dialogs_interface)

    def _header(self) -> None:
        with ui.header():
            ui.button(text = 'GO BACK', on_click = self._open_previous_url)
            ui.label('SETTINGS').classes('absolute-center')

    def _center(self) -> None:
        self.dicts.load(uuid = self.decoder.uuid)
        with ui.column().classes('w-full items-center').style('font-size:12pt'):
            with ui.tabs() as tabs:
                panel0 = ui.tab(self.ui_language.SETTINGS.Panel[0])
                panel1 = ui.tab(self.ui_language.SETTINGS.Panel[1])
                panel2 = ui.tab(self.ui_language.SETTINGS.Panel[2])
                panel3 = ui.tab(self.ui_language.SETTINGS.Panel[3])
            with ui.tab_panels(tabs, value = panel0, animated = True):
                with ui.tab_panel(panel0).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_interface().open) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.interface.help)
                    self._interface()
                with ui.tab_panel(panel1).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_replacements().open) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.replace.help)
                    self._table()
                    self._load_table()
                with ui.tab_panel(panel2).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_pdf_settings().open) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.help)
                    self._pdf_settings()
                    self._load_list()
                with ui.tab_panel(panel3).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_adv_settings().open) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.advanced.help)
                    self._adv_settings()

    def _interface(self) -> None:
        with ui.card().style('width:400px'):
            # TODO: add a translator connection check
            ui.checkbox(self.ui_language.SETTINGS.Interface[0]).bind_value(self.settings, 'dark_mode')
            ui.checkbox(self.ui_language.SETTINGS.Interface[1]).bind_value(self.settings, 'show_tips')
            ui.select(
                label = self.ui_language.SETTINGS.Interface[2],
                value = 'english',
                options = get_languages(),
                on_change = self._on_select) \
                .props('dense options-dense') \
                .style('min-width:200px; font-size:12pt') \
                .bind_value(self.settings, 'language')
            ui.input(label = 'http proxy', placeholder = 'ip-address:port').bind_value(self.settings, 'proxy_http')
            ui.input(label = 'https proxy', placeholder = 'ip-address:port').bind_value(self.settings, 'proxy_https')
            ui.button(text = 'CHECK CONNECTION', on_click = self._connection_check)
        ui.separator()
        with ui.button(text = 'APPLY', on_click = self._refresh_interface):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.interface.apply)
        with ui.button(icon = 'restore', on_click = self._reset_interface) \
                .classes('absolute-bottom-left'):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.interface.reset)

    def _table(self) -> None:
        self.ui_table = ui.table(columns = REPLACE_COLS, rows = [], row_key = 'id') \
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
                if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.replace.save)
            with ui.button(icon = 'restore', on_click = self._reset_table) \
                    .classes('absolute-bottom-left'):
                if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.replace.reset)
            with ui.button(icon = 'delete', on_click = self._clear_table) \
                    .classes('absolute-bottom-right'):
                if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.replace.delete)

    def _pdf_settings(self) -> None:
        self.ui_list = ui.table(columns = PDF_COLS, rows = [], row_key = 'id') \
            .props('hide-header separator=none') \
            .style('min-width:400px')
        self.ui_list.add_slot('body', LIST.BODY)
        self.ui_list.on('_upd_param', self._upd_param)
        ui.separator()
        with ui.button(icon = 'save', on_click = self._update_pdf_params):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.save)
        with ui.button(icon = 'restore', on_click = self._reset_list) \
                .classes('absolute-bottom-left'):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.reset)

    def _adv_settings(self) -> None:
        with ui.card().style('gap: 0.0rem; font-size:10pt'):
            ui.label(self.ui_language.SETTINGS.Advanced[0])
            self.ui_punctuations = ui.input(value = self.decoder.punctuations) \
                .style('width:400px; font-size:12pt')
            ui.space().style('height:15px')
            ui.label(self.ui_language.SETTINGS.Advanced[1])
            self.ui_beg_patterns = ui.input(value = self.decoder.beg_patterns) \
                .style('width:400px; font-size:12pt')
            ui.space().style('height:15px')
            ui.label(self.ui_language.SETTINGS.Advanced[2])
            self.ui_end_patterns = ui.input(value = self.decoder.end_patterns) \
                .style('width:400px; font-size:12pt')
            ui.space().style('height:15px')
            ui.label(self.ui_language.SETTINGS.Advanced[3])
            self.ui_quo_patterns = ui.input(value = self.decoder.quo_patterns) \
                .style('width:400px; font-size:12pt')
        ui.separator()
        with ui.button(icon = 'save', on_click = self._update_patterns):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.advanced.save)
        with ui.button(icon = 'restore', on_click = self._reset_patterns) \
                .classes('absolute-bottom-left'):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.reset)

    def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
