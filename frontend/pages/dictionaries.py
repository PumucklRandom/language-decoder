from nicegui import ui
from backend.config.config import URLS
from backend.dicts.dictonaries import Dicts
from frontend.pages.ui_custom import ui_dialog, UITable, DICT_COLS
from frontend.pages.page_abc import Page


class Dictionaries(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.DICTIONARIES)
        self.dicts: Dicts = Dicts()
        self.ui_check: ui.checkbox = None  # noqa
        self.ui_selector: ui.select = None  # noqa
        self.ui_table: UITable = None  # noqa

    def _open_previous_url(self) -> None:
        self._save_dict()
        self.update_url_history()
        i = 1 if self.url_history[0] == self.URL else 0
        ui.open(f'{self.url_history[i]}')

    def _open_settings(self) -> None:
        self._save_dict()
        self.update_url_history()
        ui.open(f'{URLS.SETTINGS}')

    def _clear_table(self) -> None:
        self.dicts.dictionaries.get(self.decoder.dict_name, {}).clear()
        self.ui_table.rows.clear()
        self.ui_table.update()

    def _delete_table(self) -> None:
        self._remove_select_option(self.decoder.dict_name)
        self.dicts.dictionaries.pop(self.decoder.dict_name, {})
        self.ui_selector.set_value(None)

    def _load_table(self) -> None:
        self.ui_table.load_table(self.dicts.dictionaries.get(self.decoder.dict_name, {}))

    def _select_table(self) -> None:
        if self.ui_selector:
            if self.ui_selector.value:
                if self.ui_check.value:
                    self._rename_table()
                else:
                    self._update_dict()
                    self.decoder.dict_name = self.ui_selector.value
                    if self.decoder.dict_name not in self.dicts.dictionaries.keys():
                        self.dicts.dictionaries[self.decoder.dict_name] = {}
                    self._load_table()
                    self.dicts.save(uuid = self.decoder.uuid)
            else:
                self._deselect_table()

    def _rename_table(self):
        self.ui_check.value = False
        self._remove_select_option(self.decoder.dict_name)
        self.dicts.dictionaries.pop(self.decoder.dict_name, {})
        self.decoder.dict_name = self.ui_selector.value
        self._save_dict()
        self.ui_selector.update()

    def _deselect_table(self):
        self.decoder.dict_name = None
        self.ui_table.rows.clear()
        self.ui_table.update()

    def _remove_select_option(self, option):
        if option in self.ui_selector.options:
            self.ui_selector.options.remove(option)

    def _save_dict(self) -> None:
        self._update_dict()
        self.dicts.save(uuid = self.decoder.uuid)

    def _update_dict(self) -> None:
        if self.decoder.dict_name:
            self.dicts.dictionaries[self.decoder.dict_name] = self.ui_table.get_values(as_dict = True)

    def _dialog_select(self) -> ui_dialog:
        return ui_dialog(label_list = self.ui_language.DICTIONARY.Dialogs_select)

    def _dialog_table(self) -> ui_dialog:
        return ui_dialog(label_list = self.ui_language.DICTIONARY.Dialogs_table)

    def _header(self) -> None:
        with ui.header():
            ui.button(text = 'GO BACK', on_click = self._open_previous_url)
            ui.label('DICTIONARIES').classes('absolute-center')
            ui.space()
            ui.button(icon = 'settings', on_click = self._open_settings)

    def _center(self) -> None:
        self.dicts.load(uuid = self.decoder.uuid)
        with ui.column().classes('w-full items-center').style('font-size:12pt'):
            with ui.card().style('width:500px'):
                self.ui_check = ui.checkbox(text = self.ui_language.DICTIONARY.Selector[0]).props('dense')
                # TODO: disable filtering options on rename
                self.ui_selector = ui.select(
                    label = self.ui_language.DICTIONARY.Selector[1],
                    value = self.decoder.dict_name,
                    options = list(self.dicts.dictionaries.keys()),
                    with_input = True,
                    new_value_mode = 'add-unique',
                    on_change = self._select_table,
                    clearable = True) \
                    .props() \
                    .style('width:350px')
                with ui.button(icon = 'help', on_click = self._dialog_select().open) \
                        .classes('absolute-top-right'):
                    if self.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.help)
                with ui.button(icon = 'delete', on_click = self._delete_table) \
                        .classes('absolute-bottom-right'):
                    if self.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.delete)

            with ui.card().classes('items-center').style('width:650px'):
                with ui.element():  # is somehow needed for the table border
                    self._table()
                with ui.button(icon = 'help', on_click = self._dialog_table().open) \
                        .classes('absolute-top-right'):
                    if self.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.help_table)
                with ui.button(icon = 'delete', on_click = self._clear_table) \
                        .classes('absolute-bottom-right'):
                    if self.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.delete_table)

    def _table(self) -> None:
        self.ui_table = UITable(columns = DICT_COLS).style('min-width:500px; max-height:80vh')
        self._load_table()

    def _footer(self) -> None:
        with ui.footer():
            ui.space()
            with ui.button(text = 'IMPORT', on_click = None):
                if self.show_tips: ui.tooltip('Import dictionary')
            ui.space()
            with ui.button(icon = 'save', on_click = self._save_dict):
                if self.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.save)
            ui.space()
            with ui.button(text = 'EXPORT', on_click = None):
                if self.show_tips: ui.tooltip('Export dictionary')
            ui.space()

    def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
        self._footer()
