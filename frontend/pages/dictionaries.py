import pathlib
from nicegui import ui, events
from backend.error.error import DictionaryError
from frontend.pages.ui.error import catch
from frontend.pages.ui.config import URLS, DICT_COLS
from frontend.pages.ui.custom import ui_dialog, UITable, UIUpload
from frontend.pages.ui.page_abc import Page


class Dictionaries(Page):
    __slots__ = (
        '_ui_selector',
        '_ui_table',
        '_rename'
    )

    _URL = URLS.DICTIONARIES

    def __init__(self) -> None:
        super().__init__()
        self._ui_selector: ui.select
        self._ui_table: UITable
        self._rename: bool = False

    @catch
    def _select_table(self) -> None:
        if not self._ui_selector.value:
            self._deselect_table()
            return
        if self._rename:
            self._rename_table()
            return
        self._get_dict_values()
        self.dicts.dict_name = self._ui_selector.value
        self._set_dict_values()

    @catch
    def _deselect_table(self) -> None:
        self._get_dict_values()
        self.dicts.dict_name = None
        self._ui_table.rows.clear()
        self._ui_table.update()

    @catch
    def _rename_table(self) -> None:
        self._rename = False
        self._remove_select_option(self.dicts.dict_name)
        self.dicts.dictionaries.pop(self.dicts.dict_name, {})
        self.dicts.dict_name = self._ui_selector.value
        self._ui_selector.update()
        self._get_dict_values()

    @catch
    def _remove_select_option(self, option: str) -> None:
        if option in self._ui_selector.options:
            self._ui_selector.options.remove(option)

    @catch
    def _get_dict_values(self) -> None:
        if self.dicts.dict_name:
            self.dicts.dictionaries[self.dicts.dict_name] = self._ui_table.get_values(as_dict = True)
        if not self._ui_selector.value: return
        if self._ui_selector.value not in self.dicts.dictionaries.keys():
            self.dicts.dictionaries[self._ui_selector.value] = self._ui_table.get_values(as_dict = True)

    @catch
    def _save_dict(self) -> None:
        self._get_dict_values()
        self.dicts.save()

    @catch
    def _delete_table(self) -> None:
        self._remove_select_option(self.dicts.dict_name)
        self.dicts.dictionaries.pop(self.dicts.dict_name, {})
        self.dicts.dict_name = None
        self._ui_selector.set_value(None)

    @catch
    def _clear_table(self) -> None:
        self.dicts.dictionaries.get(self.dicts.dict_name, {}).clear()
        self._ui_table.rows.clear()
        self._ui_table.update()

    @catch
    def _set_dict_values(self) -> None:
        if self.dicts.dict_name:
            self._ui_table.set_values(self.dicts.dictionaries.setdefault(self.dicts.dict_name, {}))

    def _get_table_page(self) -> None:
        self.state.table_page = self._ui_table.pagination

    @catch
    def _dialog_select(self) -> None:
        ui_dialog(label_list = self.UI_LABELS.DICTIONARY.Dialogs_select).open()

    @catch
    def _dialog_table(self) -> None:
        ui_dialog(label_list = self.UI_LABELS.DICTIONARY.Dialogs_table).open()

    @catch
    async def _export(self) -> None:
        if not self.dicts.dict_name: return
        self._get_dict_values()
        content = self.dicts.to_json_str(dict_name = self.dicts.dict_name)
        await self.open_route(
            content = content,
            file_type = 'json',
            filename = self.dicts.dict_name
        )

    @catch
    def _on_upload_reject(self) -> None:
        ui.notify(f'{self.UI_LABELS.DICTIONARY.Messages.reject} {self.max_file_size / 10 ** 3} KB.',
                  type = 'warning', position = 'top')

    @catch
    def _upload_handler(self, event: events.UploadEventArguments) -> None:
        try:
            data = event.content.read().decode('utf-8')
            dict_name = pathlib.Path(event.name).stem
            self.dicts.from_json_str(dict_name = dict_name, data = data)
            self._ui_selector._handle_new_value(dict_name)  # noqa: required to add new value to selection list
            self._ui_selector.set_value(dict_name)
            self._set_dict_values()
        except DictionaryError:
            ui.notify(self.UI_LABELS.DICTIONARY.Messages.invalid, type = 'warning', position = 'top')
        finally:
            event.sender.reset()  # noqa upload reset

    @catch
    def _import(self) -> None:
        with ui.dialog() as dialog:
            with ui.card().classes('items-center').style('font-size:12pt'):
                ui.button(icon = 'close', on_click = dialog.close) \
                    .classes('absolute-top-right') \
                    .props('dense round size=12px')
                ui.label(text = self.UI_LABELS.DICTIONARY.Dialogs_import[0])
                UIUpload(
                    text = self.UI_LABELS.DICTIONARY.Dialogs_import[1],
                    on_upload = self._upload_handler,
                    on_rejected = self._on_upload_reject,
                    max_file_size = self.max_file_size,
                    auto_upload = self.auto_upload,
                    max_files = self.max_files) \
                    .props('accept=.json')
            dialog.open()

    @catch
    def _header(self) -> None:
        with ui.header():
            with ui.button(icon = 'keyboard_backspace',
                           on_click = lambda: self.goto('back', call = self._save_dict)):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DICTIONARY.Tips.back)
            ui.label(self.UI_LABELS.DICTIONARY.Header.dictionaries) \
                .classes('absolute-center').style('font-size:14pt')
            ui.space()
            ui.button(icon = 'settings', on_click = lambda: self.goto(URLS.SETTINGS, call = self._save_dict))

    @catch
    def _center(self) -> None:
        self.dicts.load()
        with ui.column().classes('w-full items-center'):
            self._selector()
            with ui.card().classes('items-center').style('width:700px'):
                with ui.element():  # is somehow needed for the table border
                    self._table()
                with ui.button(icon = 'help', on_click = self._dialog_table) \
                        .classes('absolute-top-right'):
                    if self.show_tips: ui.tooltip(self.UI_LABELS.DICTIONARY.Tips.help)
                with ui.button(icon = 'delete', on_click = self._clear_table) \
                        .classes('absolute-bottom-right'):
                    if self.show_tips: ui.tooltip(self.UI_LABELS.DICTIONARY.Tips.clear)

    @catch
    def _selector(self) -> None:
        with ui.card().style('width:545px'):
            ui.checkbox(
                text = self.UI_LABELS.DICTIONARY.Selector.rename) \
                .props('dense').bind_value(self, '_rename')
            self._ui_selector = ui.select(
                label = self.UI_LABELS.DICTIONARY.Selector.select,
                value = self.dicts.dict_name,
                options = list(self.dicts.dictionaries.keys()),
                with_input = True,
                new_value_mode = 'add-unique',
                on_change = self._select_table,
                clearable = True) \
                .style('width:400px; font-size:13pt') \
                .props('outlined popup-content-style="font-size: 11pt"')
            with ui.button(icon = 'help', on_click = self._dialog_select) \
                    .classes('absolute-top-right'):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DICTIONARY.Tips.help)
            with ui.button(icon = 'delete', on_click = self._delete_table) \
                    .classes('absolute-bottom-right'):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DICTIONARY.Tips.delete)

    @catch
    def _table(self) -> None:
        DICT_COLS[0].update({'label': self.UI_LABELS.DICTIONARY.Table.key})
        DICT_COLS[1].update({'label': self.UI_LABELS.DICTIONARY.Table.val})
        self._ui_table = UITable(
            columns = DICT_COLS,
            dark_mode = self.settings.app.dark_mode,
            pagination = self.state.table_page,
            on_pagination_change = self._get_table_page) \
            .classes('sticky-header').style('min-width:550px; max-height:75vh')
        self._set_dict_values()

    @catch
    def _footer(self) -> None:
        with ui.footer():
            ui.space()
            with ui.button(text = self.UI_LABELS.DICTIONARY.Footer.import_, on_click = self._import):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DICTIONARY.Tips.import_)
            ui.space()
            with ui.button(icon = 'save', on_click = self._save_dict):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DICTIONARY.Tips.save)
            ui.space()
            with ui.button(text = self.UI_LABELS.DICTIONARY.Footer.export, on_click = self._export):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DICTIONARY.Tips.export)
            ui.space()

    async def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
        self._footer()
