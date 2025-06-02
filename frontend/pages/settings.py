from copy import copy
from nicegui import ui, Client
from backend.config.config import CONFIG
from backend.error.error import DecoderError
from frontend.pages.ui.config import URLS, REPLACE_COLS, get_languages
from frontend.pages.ui.error import catch
from frontend.pages.ui.custom import ui_dialog, UITable, UIList
from frontend.pages.ui.page_abc import Page


class Settings(Page):
    _URL = URLS.SETTINGS

    def __init__(self) -> None:
        super().__init__()
        self.ui_table: UITable
        self.ui_pdf_list: UIList
        self.ui_adv_list: UIList

    @catch
    def _save_settings(self) -> None:
        self._get_replacements()
        self._get_pdf_values()
        self._get_adv_values()
        self.decoder.get_proxies()
        self.settings.save()

    def _reset_app_settings(self) -> None:
        self.settings.app.dark_mode = CONFIG.App.dark_mode
        self.settings.app.show_tips = CONFIG.App.show_tips
        self.settings.app.language = CONFIG.App.language
        self.settings.app.reformatting = CONFIG.App.reformatting
        self.settings.app.model_name = CONFIG.App.model_name
        self.settings.app.http = ''
        self.settings.app.https = ''

    @catch
    def _connection_check(self) -> None:
        try:
            self.decoder.get_proxies()
            self.decoder.translate(source = 'test')
            ui.notify(self.UI_LABELS.SETTINGS.Messages.connect_check,
                      type = 'positive', position = 'top')
        except DecoderError as exception:
            ui.notify(exception.message,
                      type = 'warning', position = 'top')

    @catch
    def _clear_replacements(self) -> None:
        self.settings.replacements.clear()
        self.ui_table.rows.clear()
        self.ui_table.update()
        self._get_replacements()

    @catch
    def _reset_replacements(self) -> None:
        self.settings.replacements = CONFIG.Replacements.copy()
        self.ui_table.set_values(self.settings.replacements)
        self._get_replacements()

    @catch
    def _get_replacements(self) -> None:
        self.settings.replacements = self.ui_table.get_values(as_dict = True)

    @catch
    def _set_pdf_values(self) -> None:
        self.ui_pdf_list.set_values(
            self.UI_LABELS.SETTINGS.Pdf, self.settings.pdf_params.values()
        )

    @catch
    def _reset_pdf_list(self) -> None:
        self.settings.pdf_params = CONFIG.Pdf_params._asdict()
        self._set_pdf_values()

    @catch
    def _get_pdf_values(self) -> None:
        _, values = self.ui_pdf_list.get_values()
        for key, val in zip(self.settings.pdf_params.keys(), values):
            if key == 'page_per_sheet':
                self.settings.pdf_params[key] = int(val)
            elif key == 'page_sep':
                self.settings.pdf_params[key] = bool(val)
            elif key in ['tab_size', 'char_lim', 'line_lim']:
                self.settings.pdf_params[key] = int(abs(val))
            elif key in ['top_margin', 'left_margin']:
                self.settings.pdf_params[key] = val
            else:
                self.settings.pdf_params[key] = abs(val)

    @catch
    def _set_adv_values(self) -> None:
        self.ui_adv_list.set_values(
            self.UI_LABELS.SETTINGS.Advanced, self.settings.regex._asdict().values()
        )

    @catch
    def _reset_adv_list(self) -> None:
        self.settings.regex = copy(CONFIG.Regex)
        self._set_adv_values()

    @catch
    def _get_adv_values(self) -> None:
        _, values = self.ui_adv_list.get_values()
        self.settings.regex = CONFIG.Regex._make(values)

    @catch
    def _dialog_app_settings(self) -> None:
        ui_dialog(label_list = self.UI_LABELS.SETTINGS.Dialogs_app).open()

    @catch
    def _dialog_replacements(self) -> None:
        ui_dialog(label_list = self.UI_LABELS.SETTINGS.Dialogs_replace).open()

    @catch
    def _dialog_pdf_settings(self) -> None:
        ui_dialog(label_list = self.UI_LABELS.SETTINGS.Dialogs_pdf).open()

    @catch
    def _dialog_adv_settings(self) -> None:
        ui_dialog(label_list = self.UI_LABELS.SETTINGS.Dialogs_adv).open()

    @catch
    def _header(self) -> None:
        with ui.header():
            with ui.button(icon = 'keyboard_backspace',
                           on_click = lambda: self.goto('back', call = self._save_settings)):
                if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.back)
            ui.label(self.UI_LABELS.SETTINGS.Header.settings).classes('absolute-center')

    @catch
    def _center(self) -> None:
        with ui.column().style('font-size:12pt').classes('w-full items-center'):
            with ui.tabs() as tabs:
                panel0 = ui.tab(self.UI_LABELS.SETTINGS.Panel[0])
                panel1 = ui.tab(self.UI_LABELS.SETTINGS.Panel[1])
                panel2 = ui.tab(self.UI_LABELS.SETTINGS.Panel[2])
                panel3 = ui.tab(self.UI_LABELS.SETTINGS.Panel[3])
            with ui.tab_panels(tabs, value = panel0, animated = True):
                with ui.tab_panel(panel0).style('min-width:650px').classes('items-center'):
                    with ui.button(icon = 'help', on_click = self._dialog_app_settings) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.app.help)
                    self._app_settings()
                with ui.tab_panel(panel1).style('min-width:650px').classes('items-center'):
                    with ui.button(icon = 'help', on_click = self._dialog_replacements) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.replace.help)
                    self._replacements()
                with ui.tab_panel(panel2).style('min-width:650px').classes('items-center'):
                    with ui.button(icon = 'help', on_click = self._dialog_pdf_settings) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.pdf.help)
                    self._pdf_settings()
                with ui.tab_panel(panel3).style('min-width:650px').classes('items-center'):
                    with ui.button(icon = 'help', on_click = self._dialog_adv_settings) \
                            .classes('absolute-top-right'):
                        if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.advanced.help)
                    self._adv_settings()

    @catch
    def _app_settings(self) -> None:
        with ui.card().classes('items-center').style('width:420px'):
            with ui.column():
                ui.checkbox(self.UI_LABELS.SETTINGS.App_settings.text[0]) \
                    .style('min-width:240px').bind_value(self.settings.app, 'dark_mode')
                ui.checkbox(self.UI_LABELS.SETTINGS.App_settings.text[1]) \
                    .style('min-width:240px').bind_value(self.settings.app, 'show_tips')
                ui.select(
                    label = self.UI_LABELS.SETTINGS.App_settings.text[2],
                    options = get_languages(),
                    on_change = self.get_ui_labels) \
                    .props('dense options-dense outlined') \
                    .style('min-width:240px; font-size:12pt') \
                    .bind_value(self.settings.app, 'language')
            ui.separator()
            ui.checkbox(self.UI_LABELS.SETTINGS.App_settings.text[3]) \
                .style('min-width:240px').bind_value(self.settings.app, 'reformatting')
            ui.select(label = self.UI_LABELS.SETTINGS.App_settings.text[4],
                      options = self.decoder.models) \
                .props('options-dense outlined') \
                .style('min-width:380px; font-size:12pt') \
                .bind_value(self.settings.app, 'model_name')
            ui.separator()
            ui.label(text = self.UI_LABELS.SETTINGS.App_settings.text[5])
            ui.input(label = 'http proxy', placeholder = 'ip-address:port') \
                .style('min-width:240px').bind_value(self.settings.app, 'http')
            ui.input(label = 'https proxy', placeholder = 'ip-address:port') \
                .style('min-width:240px').bind_value(self.settings.app, 'https')
            ui.button(text = self.UI_LABELS.SETTINGS.App_settings.check, on_click = self._connection_check)
        ui.separator()
        with ui.button(text = self.UI_LABELS.SETTINGS.App_settings.reload, on_click = ui.navigate.reload):
            if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.app.reload)
        with ui.button(icon = 'restore', on_click = self._reset_app_settings) \
                .classes('absolute-bottom-left'):
            if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.app.reset)

    @catch
    def _replacements(self) -> None:
        REPLACE_COLS[0].update({'label': self.UI_LABELS.SETTINGS.Table.key})
        REPLACE_COLS[1].update({'label': self.UI_LABELS.SETTINGS.Table.val})
        self.ui_table = UITable(
            columns = REPLACE_COLS,
            dark_mode = self.settings.app.dark_mode) \
            .classes('sticky-header').style('min-width:420px; max-height:80vh')
        ui.separator()
        with ui.row():
            with ui.button(icon = 'save', on_click = self._get_replacements):
                if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.replace.save)
            with ui.button(icon = 'restore', on_click = self._reset_replacements) \
                    .classes('absolute-bottom-left'):
                if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.replace.reset)
            with ui.button(icon = 'delete', on_click = self._clear_replacements) \
                    .classes('absolute-bottom-right'):
                if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.replace.delete)
        self.ui_table.set_values(self.settings.replacements)

    @catch
    def _pdf_settings(self) -> None:
        self.ui_pdf_list = UIList(val_type = 'number')
        ui.separator()
        with ui.button(icon = 'save', on_click = self._get_pdf_values):
            if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.pdf.save)
        with ui.button(icon = 'restore', on_click = self._reset_pdf_list) \
                .classes('absolute-bottom-left'):
            if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.pdf.reset)
        self._set_pdf_values()

    @catch
    def _adv_settings(self) -> None:
        self.ui_adv_list = UIList(val_type = 'text')
        ui.separator()
        with ui.button(icon = 'save', on_click = self._get_adv_values):
            if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.advanced.save)
        with ui.button(icon = 'restore', on_click = self._reset_adv_list) \
                .classes('absolute-bottom-left'):
            if self.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.pdf.reset)
        self._set_adv_values()

    async def page(self, client: Client) -> None:
        await self.__init_ui__(client = client)
        self._header()
        self._center()
