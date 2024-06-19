import pathlib
import traceback
from nicegui import ui, events, Client
from backend.error.error import DictionaryError
from backend.logger.logger import logger
from backend.dicts.dictonaries import Dicts
from frontend.pages.ui.config import URLS, DICT_COLS
from frontend.pages.ui.custom import ui_dialog, UITable
from frontend.pages.ui.page_abc import Page


class Dictionaries(Page):
    _URL = URLS.DICTIONARIES

    def __init__(self) -> None:
        super().__init__()
        self.dicts: Dicts = Dicts()
        self.ui_rename_flag: ui.checkbox = None  # noqa
        self.ui_selector: ui.select = None  # noqa
        self.ui_table: UITable = None  # noqa

    def _go_back(self) -> None:
        try:
            self._save_dict()
            ui.navigate.back()
        except Exception:
            logger.error(f'Error in "_go_back" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _go_to_settings(self) -> None:
        try:
            self._save_dict()
            ui.navigate.to(f'{URLS.SETTINGS}')
        except Exception:
            logger.error(f'Error in "_go_to_settings" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _clear_table(self) -> None:
        try:
            self.dicts.dictionaries.get(self.state.dict_name, {}).clear()
            self.ui_table.rows.clear()
            self.ui_table.update()
            # self.dicts.save(user_uuid = self.state.user_uuid)
        except Exception:
            logger.error(f'Error in "_clear_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _delete_table(self) -> None:
        try:
            self._remove_select_option(self.state.dict_name)
            self.dicts.dictionaries.pop(self.state.dict_name, {})
            self.ui_selector.set_value(None)
            # self.dicts.save(user_uuid = self.state.user_uuid)
        except Exception:
            logger.error(f'Error in "_delete_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _load_table(self) -> None:
        try:
            self.ui_table.set_values(self.dicts.dictionaries.get(self.state.dict_name, {}))
        except Exception:
            logger.error(f'Error in "_load_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _select_table(self) -> None:
        try:
            if not self.ui_selector:
                return
            if not self.ui_selector.value:
                self._deselect_table()
                return
            if self.ui_rename_flag.value:
                self._rename_table()
                return
            self._update_dict()  # self._save_dict()
            self.state.dict_name = self.ui_selector.value
            if self.state.dict_name not in self.dicts.dictionaries.keys():
                self.dicts.dictionaries[self.state.dict_name] = {}
            self._load_table()
        except Exception:
            logger.error(f'Error in "_select_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _rename_table(self) -> None:
        try:
            self.ui_rename_flag.value = False
            self._remove_select_option(self.state.dict_name)
            self.dicts.dictionaries.pop(self.state.dict_name, {})
            self.state.dict_name = self.ui_selector.value
            self.ui_selector.update()
            # self.dicts.save(user_uuid = self.state.user_uuid)
        except Exception:
            logger.error(f'Error in "_rename_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _deselect_table(self) -> None:
        try:
            self.state.dict_name = None
            self.ui_table.rows.clear()
            self.ui_table.update()
        except Exception:
            logger.error(f'Error in "_deselect_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _remove_select_option(self, option) -> None:
        try:
            if option in self.ui_selector.options:
                self.ui_selector.options.remove(option)
        except Exception:
            logger.error(f'Error in "_remove_select_option" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _update_dict(self) -> None:
        try:
            if self.state.dict_name:
                self.dicts.dictionaries[self.state.dict_name] = self.ui_table.get_values(as_dict = True)
        except Exception:
            logger.error(f'Error in "_update_dict" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _save_dict(self) -> None:
        try:
            self._update_dict()
            self.dicts.save(user_uuid = self.state.user_uuid)
        except Exception:
            logger.error(f'Error in "_save_dict" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _dialog_select(self) -> ui_dialog:
        try:
            return ui_dialog(label_list = self.ui_language.DICTIONARY.Dialogs_select)
        except Exception:
            logger.error(f'Error in "_dialog_select" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _dialog_table(self) -> ui_dialog:
        try:
            return ui_dialog(label_list = self.ui_language.DICTIONARY.Dialogs_table)
        except Exception:
            logger.error(f'Error in "_dialog_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _export(self) -> None:
        try:
            if not self.state.dict_name:
                return
            self._save_dict()
            content = self.dicts.export(dict_name = self.state.dict_name)
            route = self.upd_app_route(
                url = URLS.DOWNLOAD,
                content = content,
                file_type = 'json',
                filename = self.state.dict_name,
            )
            ui.download(route)
        except Exception:
            logger.error(f'Error in "_export" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _on_upload_reject(self) -> None:
        try:
            ui.notify(f'{self.ui_language.DICTIONARY.Messages.reject} {self.max_file_size / 10 ** 3} KB',
                      type = 'warning', position = 'top')
        except Exception:
            logger.error(f'Error in "_on_upload_reject" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _upload_handler(self, event: events.UploadEventArguments) -> None:
        try:
            data = event.content.read().decode('utf-8')
            dict_name = pathlib.Path(event.name).stem
            self.dicts.import_(dict_name = dict_name, data = data)
            self.ui_selector._handle_new_value(dict_name)  # needed to add new value to selection list
            self.ui_selector.set_value(dict_name)
            self._load_table()
            # self._save_dict()
        except DictionaryError:
            ui.notify(self.ui_language.DICTIONARY.Messages.invalid, type = 'warning', position = 'top')
        except Exception:
            logger.error(f'Error in "_upload_handler" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')
        finally:
            event.sender.reset()  # noqa upload reset

    def _import(self) -> None:
        try:
            with ui.dialog() as dialog:
                with ui.card().classes('items-center'):
                    ui.button(icon = 'close', on_click = dialog.close) \
                        .classes('absolute-top-right') \
                        .props('dense round size=12px')
                    ui.label(text = self.ui_language.DICTIONARY.Dialogs_import[0])
                    ui.upload(
                        label = self.ui_language.DICTIONARY.Dialogs_import[1],
                        on_upload = self._upload_handler,
                        on_rejected = self._on_upload_reject,
                        max_file_size = self.max_file_size,
                        auto_upload = self.auto_upload,
                        max_files = self.max_files) \
                        .props('accept=.json flat dense')
                dialog.open()
        except Exception:
            logger.error(f'Error in "_import" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _header(self) -> None:
        try:
            with ui.header():
                ui.button(text = self.ui_language.DICTIONARY.Header.go_back, on_click = self._go_back)
                ui.label(self.ui_language.DICTIONARY.Header.dictionaries).classes('absolute-center')
                ui.space()
                ui.button(icon = 'settings', on_click = self._go_to_settings)
        except Exception:
            logger.error(f'Error in "_header" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _center(self) -> None:
        try:
            self.dicts.load(user_uuid = self.state.user_uuid)
            with ui.column().classes('w-full items-center').style('font-size:12pt'):
                self._selector()
                with ui.card().classes('items-center').style('width:650px'):
                    with ui.element():  # is somehow needed for the table border
                        self._table()
                    with ui.button(icon = 'help', on_click = self._dialog_table().open) \
                            .classes('absolute-top-right'):
                        if self.state.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.help)
                    with ui.button(icon = 'delete', on_click = self._clear_table) \
                            .classes('absolute-bottom-right'):
                        if self.state.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.clear)
        except Exception:
            logger.error(f'Error in "_center" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _selector(self):
        try:
            with ui.card().style('width:500px'):
                self.ui_rename_flag = ui.checkbox(
                    text = self.ui_language.DICTIONARY.Selector.rename).props('dense')
                # TODO: disable filtering options on rename
                self.ui_selector = ui.select(
                    label = self.ui_language.DICTIONARY.Selector.select,
                    value = self.state.dict_name,
                    options = list(self.dicts.dictionaries.keys()),
                    with_input = True,
                    new_value_mode = 'add-unique',
                    on_change = self._select_table,
                    clearable = True) \
                    .style('width:350px')
                with ui.button(icon = 'help', on_click = self._dialog_select().open) \
                        .classes('absolute-top-right'):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.help)
                with ui.button(icon = 'delete', on_click = self._delete_table) \
                        .classes('absolute-bottom-right'):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.delete)
        except Exception:
            logger.error(f'Error in "_selector" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _table(self) -> None:
        try:
            DICT_COLS[0].update({'label': self.ui_language.DICTIONARY.Table.key})
            DICT_COLS[1].update({'label': self.ui_language.DICTIONARY.Table.val})
            self.ui_table = UITable(columns = DICT_COLS, dark_mode = self.state.dark_mode) \
                .style('min-width:500px; max-height:75vh')
            self._load_table()
        except Exception:
            logger.error(f'Error in "_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _footer(self) -> None:
        try:
            with ui.footer():
                ui.space()
                with ui.button(text = self.ui_language.DICTIONARY.Footer.import_, on_click = self._import):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.import_)
                ui.space()
                with ui.button(icon = 'save', on_click = self._save_dict):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.save)
                ui.space()
                with ui.button(text = self.ui_language.DICTIONARY.Footer.export, on_click = self._export):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DICTIONARY.Tips.export)
                ui.space()
        except Exception:
            logger.error(f'Error in "_footer" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def page(self, client: Client) -> None:
        await self.__init_ui__(client = client)
        self._header()
        self._center()
        self._footer()
