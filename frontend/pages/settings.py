from nicegui import ui
from copy import copy
from backend.config.config import CONFIG, REPLACEMENTS
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.dicts.dictonaries import Dicts
from frontend.pages.ui.config import URLS, REPLACE_COLS, load_language, get_languages
from frontend.pages.ui.custom import ui_dialog, UITable, UIList
from frontend.pages.ui.page_abc import Page


class Settings(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.SETTINGS)
        self.dicts: Dicts = Dicts()
        self.ui_table: UITable = None  # noqa
        self.ui_pdf_list: UIList = None  # noqa
        self.ui_adv_list: UIList = None  # noqa

    def _open_previous_url(self) -> None:
        self._update_replacements()
        self._update_pdf_params()
        self._update_adv_params()
        # do not update url history in settings
        ui.open(f'{self.url_history[0]}')

    def _refresh_interface(self) -> None:
        self.decoder.proxies = self.settings.get_proxies()
        ui.open(f'{self.URL}')

    def _reset_interface(self) -> None:
        self.settings.dark_mode = True
        self.settings.show_tips = True
        self.decoder.reformatting = True
        self.settings.language = 'english'
        self.settings.proxy_http = ''
        self.settings.proxy_https = ''

    def _connection_check(self) -> None:
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

    def _clear_table(self) -> None:
        self.dicts.replacements.clear()
        self.ui_table.rows.clear()
        self.ui_table.update()
        self._update_replacements()

    def _reset_table(self) -> None:
        self.dicts.replacements = REPLACEMENTS.copy()
        self.ui_table.set_values(self.dicts.replacements)
        self._update_replacements()

    def _update_replacements(self) -> None:
        self.dicts.replacements = self.ui_table.get_values(as_dict = True)
        self.dicts.save(uuid = self.decoder.uuid)

    def _load_pdf_list(self) -> None:
        self.ui_pdf_list.set_values(self.ui_language.SETTINGS.Pdf, self.pdf_params.values())

    def _reset_pdf_list(self) -> None:
        self.pdf_params = CONFIG.Pdf.__dict__.copy()
        self._load_pdf_list()

    def _update_pdf_params(self) -> None:
        _, values = self.ui_pdf_list.get_values()
        for key, val in zip(self.pdf_params.keys(), values):
            if key == 'page_sep':
                if val >= 0: self.pdf_params[key] = bool(val)
            elif key in ['tab_size', 'char_lim', 'line_lim']:
                if val > 0: self.pdf_params[key] = int(val)
            else:
                if val > 0: self.pdf_params[key] = val

    def _load_adv_list(self) -> None:
        self.ui_adv_list.set_values(self.ui_language.SETTINGS.Advanced, self.decoder.regex.__dict__.values())

    def _reset_adv_list(self) -> None:
        self.decoder.regex = copy(CONFIG.Regex)
        self._load_adv_list()

    def _update_adv_params(self) -> None:
        _, values = self.ui_adv_list.get_values()
        for key, val in zip(self.decoder.regex.__dict__.keys(), values):
            self.decoder.regex.__setattr__(key, val)

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
                    self._replacements()
                with ui.tab_panel(panel2).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_pdf_settings().open) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.help)
                    self._pdf_settings()
                with ui.tab_panel(panel3).classes('items-center').style('min-width:650px'):
                    with ui.button(icon = 'help', on_click = self._dialog_adv_settings().open) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.advanced.help)
                    self._adv_settings()

    def _interface(self) -> None:
        with ui.card().style('width:400px'):
            ui.checkbox(self.ui_language.SETTINGS.Interface.text[0]).bind_value(self.settings, 'dark_mode')
            ui.checkbox(self.ui_language.SETTINGS.Interface.text[1]).bind_value(self.settings, 'show_tips')
            ui.checkbox(self.ui_language.SETTINGS.Interface.text[2]).bind_value(self.decoder, 'reformatting')
            ui.select(
                label = self.ui_language.SETTINGS.Interface.text[3],
                value = 'english',
                options = get_languages(),
                on_change = self._on_select) \
                .props('dense options-dense') \
                .style('min-width:200px; font-size:12pt') \
                .bind_value(self.settings, 'language')
            ui.separator()
            ui.label(text = self.ui_language.SETTINGS.Interface.text[4])
            ui.input(label = 'http proxy', placeholder = 'ip-address:port').bind_value(self.settings, 'proxy_http')
            ui.input(label = 'https proxy', placeholder = 'ip-address:port').bind_value(self.settings, 'proxy_https')
            ui.button(text = self.ui_language.SETTINGS.Interface.check, on_click = self._connection_check)
        ui.separator()
        with ui.button(text = self.ui_language.SETTINGS.Interface.apply, on_click = self._refresh_interface):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.interface.apply)
        with ui.button(icon = 'restore', on_click = self._reset_interface) \
                .classes('absolute-bottom-left'):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.interface.reset)

    def _replacements(self) -> None:
        REPLACE_COLS[0].update({'label': self.ui_language.DICTIONARY.Table.key})
        REPLACE_COLS[1].update({'label': self.ui_language.DICTIONARY.Table.val})
        self.ui_table = UITable(columns = REPLACE_COLS, dark_mode = self.settings.dark_mode) \
            .style('min-width:450px; max-height:80vh')
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
        self.ui_table.set_values(self.dicts.replacements)

    def _pdf_settings(self) -> None:
        self.ui_pdf_list = UIList(val_type = 'number')
        ui.separator()
        with ui.button(icon = 'save', on_click = self._update_pdf_params):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.save)
        with ui.button(icon = 'restore', on_click = self._reset_pdf_list) \
                .classes('absolute-bottom-left'):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.reset)
        self._load_pdf_list()

    def _adv_settings(self) -> None:
        self.ui_adv_list = UIList(val_type = 'text')
        ui.separator()
        with ui.button(icon = 'save', on_click = self._update_adv_params):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.advanced.save)
        with ui.button(icon = 'restore', on_click = self._reset_adv_list) \
                .classes('absolute-bottom-left'):
            if self.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.reset)
        self._load_adv_list()

    def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
