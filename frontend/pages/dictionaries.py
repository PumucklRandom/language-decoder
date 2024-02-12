from nicegui import ui, events
from backend.config.const import URLS
from backend.dicts.dictonaries import Dicts
from frontend.pages.ui_custom import ui_dialog, TABLE
from frontend.pages.page_abc import Page


class Dictionaries(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.DICTIONARIES)
        self.dicts: Dicts = Dicts()
        self.ui_selector: ui.select = None  # noqa
        self.ui_table: ui.table = None  # noqa

    def _open_previous_url(self) -> None:
        self._update_dict()
        self.update_url_history()
        i = 1 if self.url_history[0] == self.URL else 0
        ui.open(f'{self.url_history[i]}')

    def _open_settings(self) -> None:
        self._update_dict()
        self.update_url_history()
        ui.open(f'{URLS.SETTINGS}')

    def _add_row(self, event: events.GenericEventArguments) -> None:
        if not self.decoder.dict_name:
            ui.notify('Please select or create a dictionary', type = 'negative', position = 'top')
            return
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
        self.dicts.dictionaries.get(self.decoder.dict_name).clear()
        self.ui_table.rows.clear()
        self.ui_table.update()

    def _delete_table(self) -> None:
        self.ui_selector.options.remove(self.decoder.dict_name)
        self.ui_selector.update()
        self.ui_table.rows.clear()
        self.ui_table.update()
        self.dicts.dictionaries.pop(self.decoder.dict_name)
        self.decoder.dict_name = ''

    def _load_table(self) -> None:
        self.ui_table.rows.clear()
        for i, (key, val) in enumerate(self.dicts.dictionaries.get(self.decoder.dict_name, {}).items()):
            self.ui_table.rows.insert(0, {'id': i, 'key': key, 'val': val})
        self.ui_table.update()

    def _select_table(self) -> None:
        if self.ui_selector and self.ui_selector.value:
            self.decoder.dict_name = self.ui_selector.value
            if self.decoder.dict_name not in self.ui_selector.options:
                self.dicts.dictionaries[self.decoder.dict_name] = {}
            self._load_table()

    def _update_dict(self) -> None:
        keys = [row.get('key') for row in self.ui_table.rows]
        vals = [row.get('val') for row in self.ui_table.rows]
        if self.decoder.dict_name:
            self.dicts.dictionaries[self.decoder.dict_name] = dict(zip(keys, vals))
            self.dicts.dictionaries.get(self.decoder.dict_name).pop('', None)
        self.dicts.save(uuid = self.decoder.uuid)

    @staticmethod
    def _dialog_select() -> ui_dialog:
        label_list = [
            'Some tips for the user interface!'
        ]
        return ui_dialog(label_list = label_list)

    @staticmethod
    def _dialog_table() -> ui_dialog:
        label_list = [
            'Some tips for the user interface!'
        ]
        return ui_dialog(label_list = label_list)

    def _header(self) -> None:
        with ui.header():
            ui.button(text = 'GO BACK', on_click = self._open_previous_url)
            ui.label('DICTIONARIES').classes('absolute-center')
            ui.space()
            ui.button(icon = 'settings', on_click = self._open_settings)

    def _center(self) -> None:
        self.dicts.load(uuid = self.decoder.uuid)
        with ui.column().classes('w-full items-center').style('font-size:12pt'):
            with ui.card().style('width:350px'):
                with ui.row().classes('justify-between'):
                    self.ui_selector = ui.select(
                        label = 'Select or create a dictionary',
                        value = self.decoder.dict_name,
                        options = list(self.dicts.dictionaries.keys()),
                        with_input = True,
                        new_value_mode = 'add-unique',
                        on_change = self._select_table) \
                        .style('width:250px')
                    with ui.button(icon = 'help', on_click = self._dialog_select().open) \
                            .classes('absolute-top-right'):
                        ui.tooltip('Need help?')
                    with ui.button(icon = 'delete', on_click = self._delete_table) \
                            .classes('absolute-bottom-right'):
                        ui.tooltip('Delete dictionary')
            with ui.card():
                with ui.element():  # is somehow needed
                    self._table()
                self._load_table()

    def _table(self) -> None:
        columns = [
            {'label': 'Source Words', 'name': 'key', 'field': 'key', 'required': True, 'sortable': True, 'align': 'left'},
            {'label': 'Target Words', 'name': 'val', 'field': 'val', 'required': True, 'sortable': True, 'align': 'left'},
        ]
        self.ui_table = ui.table(columns = columns, rows = [], row_key = 'id') \
            .props('flat bordered separator=cell') \
            .style('min-width:450px; max-height:80vh')
        self.ui_table.add_slot('header', TABLE.HEADER)
        self.ui_table.add_slot('body', TABLE.BODY)
        self.ui_table.on('_upd_row', self._upd_row)
        self.ui_table.on('_del_row', self._del_row)
        self.ui_table.on('_add_row', self._add_row)

    def _footer(self) -> None:
        with ui.footer():
            with ui.button(icon = 'help', on_click = self._dialog_table().open):
                ui.tooltip('Need help?')
            with ui.button(icon = 'save', on_click = self._update_dict) \
                    .classes('absolute-center'):
                ui.tooltip('Save dictionary')
            ui.space()
            with ui.button(icon = 'delete', on_click = self._clear_table):
                ui.tooltip('Clear dictionary').style('width:90px')

    def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
        self._footer()
