from nicegui import ui, Client
from backend.config.config import CONFIG, REPLACEMENTS
from backend.error.error import DecoderError
from frontend.pages.ui.config import URLS, REPLACE_COLS, get_languages, get_ui_labels
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
    def _save_state(self) -> None:
        self._save_replacements()
        self._update_pdf_params()
        self._update_adv_params()
        self._get_proxies()

    @catch
    def _get_proxies(self):
        self.state.proxies = {'http': self.state.http, 'https': self.state.https}

    def _reset_interface(self) -> None:
        self.state.dark_mode = True
        self.state.show_tips = True
        self.state.reformatting = True
        self.state.alt_trans = False
        self.state.language = 'english'
        self.state.http = ''
        self.state.https = ''

    @catch
    def _connection_check(self) -> None:
        try:
            self._get_proxies()
            self.decoder.proxies = self.state.proxies
            if self.state.alt_trans:
                self.decoder.alt_trans = self.state.alt_trans
                self.decoder.translate(source = 'test', alt_trans = True)
            else:
                self.decoder.translate(source = 'test')
            ui.notify(self.UI_LABELS.SETTINGS.Messages.connect_check[0],
                      type = 'positive', position = 'top')
        except DecoderError as exception:
            ui.notify(exception.message,
                      type = 'warning', position = 'top')

    @catch
    def _on_select(self) -> None:
        self.state.ui_labels = get_ui_labels(self.state.language)

    @catch
    def _clear_table(self) -> None:
        self.dicts.replacements.clear()
        self.ui_table.rows.clear()
        self.ui_table.update()
        self._update_replacements()

    @catch
    def _reset_table(self) -> None:
        self.dicts.replacements = REPLACEMENTS.copy()
        self.ui_table.set_values(self.dicts.replacements)
        self._update_replacements()

    @catch
    def _update_replacements(self) -> None:
        self.dicts.replacements = self.ui_table.get_values(as_dict = True)

    @catch
    def _save_replacements(self) -> None:
        self._update_replacements()
        self.dicts.save()

    @catch
    def _load_pdf_list(self) -> None:
        self.ui_pdf_list.set_values(self.UI_LABELS.SETTINGS.Pdf, self.state.pdf_params.values())

    @catch
    def _reset_pdf_list(self) -> None:
        self.state.pdf_params = CONFIG.Pdf.__dict__.copy()
        self._load_pdf_list()

    @catch
    def _update_pdf_params(self) -> None:
        _, values = self.ui_pdf_list.get_values()
        for key, val in zip(self.state.pdf_params.keys(), values):
            if key == 'page_sep':
                if val >= 0: self.state.pdf_params[key] = bool(val)
            elif key in ['tab_size', 'char_lim', 'line_lim']:
                if val > 0: self.state.pdf_params[key] = int(val)
            else:
                if val > 0: self.state.pdf_params[key] = val

    @catch
    def _load_adv_list(self) -> None:
        self.ui_adv_list.set_values(self.UI_LABELS.SETTINGS.Advanced, self.state.regex.__dict__.values())

    @catch
    def _reset_adv_list(self) -> None:
        self.state.regex = CONFIG.Regex.copy()
        self._load_adv_list()

    @catch
    def _update_adv_params(self) -> None:
        _, values = self.ui_adv_list.get_values()
        for key, val in zip(self.state.regex.__dict__.keys(), values):
            self.state.regex.__setattr__(key, val)

    @catch
    def _dialog_interface(self) -> ui_dialog:
        return ui_dialog(label_list = self.UI_LABELS.SETTINGS.Dialogs_interface)

    @catch
    def _dialog_replacements(self) -> ui_dialog:
        return ui_dialog(label_list = self.UI_LABELS.SETTINGS.Dialogs_replace)

    @catch
    def _dialog_pdf_settings(self) -> ui_dialog:
        return ui_dialog(label_list = self.UI_LABELS.SETTINGS.Dialogs_pdf)

    @catch
    def _dialog_adv_settings(self) -> ui_dialog:
        return ui_dialog(label_list = self.UI_LABELS.SETTINGS.Dialogs_adv)

    @catch
    def _header(self) -> None:
        with ui.header():
            with ui.button(icon = 'keyboard_backspace',
                           on_click = lambda: self.goto('back', call = self._save_state)):
                if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.back)
            ui.label(self.UI_LABELS.SETTINGS.Header.settings).classes('absolute-center')

    @catch
    def _center(self) -> None:
        self.dicts.load()
        with ui.column().style('font-size:12pt').classes('w-full items-center'):
            with ui.tabs() as tabs:
                panel0 = ui.tab(self.UI_LABELS.SETTINGS.Panel[0])
                panel1 = ui.tab(self.UI_LABELS.SETTINGS.Panel[1])
                panel2 = ui.tab(self.UI_LABELS.SETTINGS.Panel[2])
                panel3 = ui.tab(self.UI_LABELS.SETTINGS.Panel[3])
            with ui.tab_panels(tabs, value = panel0, animated = True):
                with ui.tab_panel(panel0).style('min-width:650px').classes('items-center'):
                    with ui.button(icon = 'help', on_click = self._dialog_interface().open) \
                            .classes('absolute-top-right'):
                        if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.interface.help)
                    self._interface()
                with ui.tab_panel(panel1).style('min-width:650px').classes('items-center'):
                    with ui.button(icon = 'help', on_click = self._dialog_replacements().open) \
                            .classes('absolute-top-right'):
                        if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.replace.help)
                    self._replacements()
                with ui.tab_panel(panel2).style('min-width:650px').classes('items-center'):
                    with ui.button(icon = 'help', on_click = self._dialog_pdf_settings().open) \
                            .classes('absolute-top-right'):
                        if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.pdf.help)
                    self._pdf_settings()
                with ui.tab_panel(panel3).style('min-width:650px').classes('items-center'):
                    with ui.button(icon = 'help', on_click = self._dialog_adv_settings().open) \
                            .classes('absolute-top-right'):
                        if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.advanced.help)
                    self._adv_settings()

    @catch
    def _interface(self) -> None:
        with ui.card().style('width:400px'):
            ui.checkbox(self.UI_LABELS.SETTINGS.Interface.text[0]).bind_value(self.state, 'dark_mode')
            ui.checkbox(self.UI_LABELS.SETTINGS.Interface.text[1]).bind_value(self.state, 'show_tips')
            ui.checkbox(self.UI_LABELS.SETTINGS.Interface.text[2]).bind_value(self.state, 'reformatting')
            ui.checkbox(self.UI_LABELS.SETTINGS.Interface.text[3]).bind_value(self.state, 'alt_trans')
            ui.separator()
            ui.select(
                label = self.UI_LABELS.SETTINGS.Interface.text[4],
                options = get_languages(),
                on_change = self._on_select) \
                .props('dense options-dense outlined') \
                .style('min-width:200px; font-size:12pt') \
                .bind_value(self.state, 'language')
            ui.separator()
            ui.label(text = self.UI_LABELS.SETTINGS.Interface.text[5])
            ui.input(label = 'http proxy', placeholder = 'ip-address:port') \
                .bind_value(self.state, 'http')
            ui.input(label = 'https proxy', placeholder = 'ip-address:port') \
                .bind_value(self.state, 'https')
            ui.button(text = self.UI_LABELS.SETTINGS.Interface.check, on_click = self._connection_check)
        ui.separator()
        with ui.button(text = self.UI_LABELS.SETTINGS.Interface.reload, on_click = ui.navigate.reload):
            if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.interface.reload)
        with ui.button(icon = 'restore', on_click = self._reset_interface) \
                .classes('absolute-bottom-left'):
            if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.interface.reset)

    @catch
    def _replacements(self) -> None:
        REPLACE_COLS[0].update({'label': self.UI_LABELS.SETTINGS.Table.key})
        REPLACE_COLS[1].update({'label': self.UI_LABELS.SETTINGS.Table.val})
        self.ui_table = UITable(columns = REPLACE_COLS, dark_mode = self.state.dark_mode) \
            .style('min-width:450px; max-height:80vh').classes('sticky-header')
        ui.separator()
        with ui.row():
            with ui.button(icon = 'save', on_click = self._save_replacements):
                if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.replace.save)
            with ui.button(icon = 'restore', on_click = self._reset_table) \
                    .classes('absolute-bottom-left'):
                if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.replace.reset)
            with ui.button(icon = 'delete', on_click = self._clear_table) \
                    .classes('absolute-bottom-right'):
                if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.replace.delete)
        self.ui_table.set_values(self.dicts.replacements)

    @catch
    def _pdf_settings(self) -> None:
        self.ui_pdf_list = UIList(val_type = 'number')
        ui.separator()
        with ui.button(icon = 'save', on_click = self._update_pdf_params):
            if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.pdf.save)
        with ui.button(icon = 'restore', on_click = self._reset_pdf_list) \
                .classes('absolute-bottom-left'):
            if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.pdf.reset)
        self._load_pdf_list()

    @catch
    def _adv_settings(self) -> None:
        self.ui_adv_list = UIList(val_type = 'text')
        ui.separator()
        with ui.button(icon = 'save', on_click = self._update_adv_params):
            if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.advanced.save)
        with ui.button(icon = 'restore', on_click = self._reset_adv_list) \
                .classes('absolute-bottom-left'):
            if self.state.show_tips: ui.tooltip(self.UI_LABELS.SETTINGS.Tips.pdf.reset)
        self._load_adv_list()

    async def page(self, client: Client) -> None:
        await self.__init_ui__(client = client)
        self._header()
        self._center()
