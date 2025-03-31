import traceback
from nicegui import ui, Client
from backend.config.config import CONFIG, REPLACEMENTS
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.dicts.dictonaries import Dicts
from frontend.pages.ui.config import URLS, REPLACE_COLS, load_language, get_languages
from frontend.pages.ui.custom import ui_dialog, UITable, UIList
from frontend.pages.ui.page_abc import Page


class Settings(Page):
    _URL = URLS.SETTINGS

    def __init__(self) -> None:
        super().__init__()
        self.dicts: Dicts = Dicts()
        self.ui_table: UITable
        self.ui_pdf_list: UIList
        self.ui_adv_list: UIList

    def _save_settings(self):
        self._save_replacements()
        self._update_pdf_params()
        self._update_adv_params()
        self.state.proxies = self.get_proxies()

    def get_proxies(self):
        return {'http': self.state.http, 'https': self.state.https}

    def _reset_interface(self) -> None:
        try:
            self.state.dark_mode = True
            self.state.show_tips = True
            self.state.reformatting = True
            self.state.alt_trans = False
            self.state.language = 'english'
            self.state.http = ''
            self.state.https = ''
        except Exception:
            logger.error(f'Error in "_reset_interface" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _connection_check(self) -> None:
        try:
            self.state.proxies = self.get_proxies()
            self.decoder.proxies = self.state.proxies
            if self.state.alt_trans:
                self.decoder.alt_trans = self.state.alt_trans
                self.decoder.translate(source = 'test', alt_trans = True)
            else:
                self.decoder.translate(source = 'test')
            ui.notify(self.ui_language.SETTINGS.Messages.connect_check[0],
                      type = 'positive', position = 'top')
        except DecoderError as exception:
            ui.notify(exception.message,
                      type = 'warning', position = 'top')
        except Exception:
            message = 'Connection failed!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.SETTINGS.Messages.connect_check[1], type = 'warning', position = 'top')

    def _on_select(self) -> None:
        try:
            self.state.ui_language = load_language(self.state.language)
        except Exception:
            logger.error(f'Error in "_on_select" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _clear_table(self) -> None:
        try:
            self.dicts.replacements.clear()
            self.ui_table.rows.clear()
            self.ui_table.update()
            # self._save_replacements()
        except Exception:
            logger.error(f'Error in "_clear_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _reset_table(self) -> None:
        try:
            self.dicts.replacements = REPLACEMENTS.copy()
            self.ui_table.set_values(self.dicts.replacements)
            # self._save_replacements()
        except Exception:
            logger.error(f'Error in "_reset_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _save_replacements(self) -> None:
        try:
            self.dicts.replacements = self.ui_table.get_values(as_dict = True)
            self.dicts.save(user_uuid = self.state.user_uuid)
        except Exception:
            logger.error(f'Error in "_update_replacements" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _load_pdf_list(self) -> None:
        try:
            self.ui_pdf_list.set_values(self.ui_language.SETTINGS.Pdf, self.state.pdf_params.values())
        except Exception:
            logger.error(f'Error in "_load_pdf_list" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _reset_pdf_list(self) -> None:
        try:
            self.state.pdf_params = CONFIG.Pdf.__dict__.copy()
            self._load_pdf_list()
        except Exception:
            logger.error(f'Error in "_reset_pdf_list" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _update_pdf_params(self) -> None:
        try:
            _, values = self.ui_pdf_list.get_values()
            for key, val in zip(self.state.pdf_params.keys(), values):
                if key == 'page_sep':
                    if val >= 0: self.state.pdf_params[key] = bool(val)
                elif key in ['tab_size', 'char_lim', 'line_lim']:
                    if val > 0: self.state.pdf_params[key] = int(val)
                else:
                    if val > 0: self.state.pdf_params[key] = val
        except Exception:
            logger.error(f'Error in "_update_pdf_params" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _load_adv_list(self) -> None:
        try:
            self.ui_adv_list.set_values(self.ui_language.SETTINGS.Advanced, self.state.regex.__dict__.values())
        except Exception:
            logger.error(f'Error in "_load_adv_list" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _reset_adv_list(self) -> None:
        try:
            self.state.regex = CONFIG.Regex.copy()
            self._load_adv_list()
        except Exception:
            logger.error(f'Error in "_reset_adv_list" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _update_adv_params(self) -> None:
        try:
            _, values = self.ui_adv_list.get_values()
            for key, val in zip(self.state.regex.__dict__.keys(), values):
                self.state.regex.__setattr__(key, val)
        except Exception:
            logger.error(f'Error in "_update_adv_params" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _dialog_interface(self) -> ui_dialog:
        try:
            return ui_dialog(label_list = self.ui_language.SETTINGS.Dialogs_interface)
        except Exception:
            logger.error(f'Error in "_dialog_interface" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _dialog_replacements(self) -> ui_dialog:
        try:
            return ui_dialog(label_list = self.ui_language.SETTINGS.Dialogs_replace)
        except Exception:
            logger.error(f'Error in "_dialog_replacements" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _dialog_pdf_settings(self) -> ui_dialog:
        try:
            return ui_dialog(label_list = self.ui_language.SETTINGS.Dialogs_pdf)
        except Exception:
            logger.error(f'Error in "_dialog_pdf_settings" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _dialog_adv_settings(self) -> ui_dialog:
        try:
            return ui_dialog(label_list = self.ui_language.SETTINGS.Dialogs_adv)
        except Exception:
            logger.error(f'Error in "_dialog_adv_settings" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _header(self) -> None:
        try:
            with ui.header():
                ui.button(text = 'GO BACK', on_click = lambda: self.goto('back', call = self._save_settings))
                ui.label('SETTINGS').classes('absolute-center')
        except Exception:
            logger.error(f'Error in "_header" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _center(self) -> None:
        try:
            self.dicts.load(user_uuid = self.state.user_uuid)
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
                            if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.interface.help)
                        self._interface()
                    with ui.tab_panel(panel1).classes('items-center').style('min-width:650px'):
                        with ui.button(icon = 'help', on_click = self._dialog_replacements().open) \
                                .classes('absolute-top-right'):
                            if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.replace.help)
                        self._replacements()
                    with ui.tab_panel(panel2).classes('items-center').style('min-width:650px'):
                        with ui.button(icon = 'help', on_click = self._dialog_pdf_settings().open) \
                                .classes('absolute-top-right'):
                            if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.help)
                        self._pdf_settings()
                    with ui.tab_panel(panel3).classes('items-center').style('min-width:650px'):
                        with ui.button(icon = 'help', on_click = self._dialog_adv_settings().open) \
                                .classes('absolute-top-right'):
                            if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.advanced.help)
                        self._adv_settings()
        except Exception:
            logger.error(f'Error in "_center" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _interface(self) -> None:
        try:
            with ui.card().style('width:400px'):
                ui.checkbox(self.ui_language.SETTINGS.Interface.text[0]).bind_value(self.state, 'dark_mode')
                ui.checkbox(self.ui_language.SETTINGS.Interface.text[1]).bind_value(self.state, 'show_tips')
                ui.checkbox(self.ui_language.SETTINGS.Interface.text[2]).bind_value(self.state, 'reformatting')
                ui.checkbox(self.ui_language.SETTINGS.Interface.text[3]).bind_value(self.state, 'alt_trans')
                ui.separator()
                ui.select(
                    label = self.ui_language.SETTINGS.Interface.text[4],
                    options = get_languages(),
                    on_change = self._on_select) \
                    .props('dense options-dense') \
                    .style('min-width:200px; font-size:12pt') \
                    .bind_value(self.state, 'language')
                ui.separator()
                ui.label(text = self.ui_language.SETTINGS.Interface.text[5])
                ui.input(label = 'http proxy', placeholder = 'ip-address:port') \
                    .bind_value(self.state, 'http')
                ui.input(label = 'https proxy', placeholder = 'ip-address:port') \
                    .bind_value(self.state, 'https')
                ui.button(text = self.ui_language.SETTINGS.Interface.check, on_click = self._connection_check)
            ui.separator()
            with ui.button(text = self.ui_language.SETTINGS.Interface.reload, on_click = ui.navigate.reload):
                if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.interface.reload)
            with ui.button(icon = 'restore', on_click = self._reset_interface) \
                    .classes('absolute-bottom-left'):
                if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.interface.reset)
        except Exception:
            logger.error(f'Error in "_interface" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _replacements(self) -> None:
        try:
            REPLACE_COLS[0].update({'label': self.ui_language.SETTINGS.Table.key})
            REPLACE_COLS[1].update({'label': self.ui_language.SETTINGS.Table.val})
            self.ui_table = UITable(columns = REPLACE_COLS, dark_mode = self.state.dark_mode) \
                .style('min-width:450px; max-height:80vh')
            ui.separator()
            with ui.row():
                with ui.button(icon = 'save', on_click = self._save_replacements):
                    if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.replace.save)
                with ui.button(icon = 'restore', on_click = self._reset_table) \
                        .classes('absolute-bottom-left'):
                    if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.replace.reset)
                with ui.button(icon = 'delete', on_click = self._clear_table) \
                        .classes('absolute-bottom-right'):
                    if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.replace.delete)
            self.ui_table.set_values(self.dicts.replacements)
        except Exception:
            logger.error(f'Error in "_replacements" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _pdf_settings(self) -> None:
        try:
            self.ui_pdf_list = UIList(val_type = 'number')
            ui.separator()
            with ui.button(icon = 'save', on_click = self._update_pdf_params):
                if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.save)
            with ui.button(icon = 'restore', on_click = self._reset_pdf_list) \
                    .classes('absolute-bottom-left'):
                if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.reset)
            self._load_pdf_list()
        except Exception:
            logger.error(f'Error in "_pdf_settings" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _adv_settings(self) -> None:
        try:
            self.ui_adv_list = UIList(val_type = 'text')
            ui.separator()
            with ui.button(icon = 'save', on_click = self._update_adv_params):
                if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.advanced.save)
            with ui.button(icon = 'restore', on_click = self._reset_adv_list) \
                    .classes('absolute-bottom-left'):
                if self.state.show_tips: ui.tooltip(self.ui_language.SETTINGS.Tips.pdf.reset)
            self._load_adv_list()
        except Exception:
            logger.error(f'Error in "_adv_settings" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def page(self, client: Client) -> None:
        await self.__init_ui__(client = client)
        self._header()
        self._center()
