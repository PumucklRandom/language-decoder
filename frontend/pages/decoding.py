import asyncio
from typing import List
from nicegui import ui, events
from backend.config.const import URLS
from backend.decoder.pdf import PDF
from frontend.pages.ui_config import LENF
from frontend.pages.page_abc import Page

'''
Der schnelle braune Fuchs, springt über den großen faulen Hund.
Der schnelle braune Fuchs, springt über den großen faulen Hund.
Der schnelle braune Fuchs, springt über den großen faulen Hund.
Der schnelle braune Fuchs, springt über den großen faulen Hund.
Der schnelle braune Fuchs, springt über den großen faulen Hund.
'''


class Decoding(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.DECODING)
        self._pdf: PDF = PDF()
        self.ui_table: ui.table = None
        self.s_hash: int = 0
        self.d_hash: int = 0

    def _open_upload(self) -> None:
        self._update_words()
        self.update_url_history()
        ui.open(f'{URLS.UPLOAD}')

    def _open_dictionaries(self) -> None:
        self._update_words()
        self.update_url_history()
        ui.open(f'{URLS.DICTIONARIES}')

    def _open_settings(self) -> None:
        self._update_words()
        self.update_url_history()
        ui.open(f'{URLS.SETTINGS}')

    def _upd_row(self, event: events.GenericEventArguments) -> None:
        for row in self.ui_table.rows:
            if row.get('id') == event.args.get('id'):
                row.update(event.args)

    def _load_table(self) -> None:
        self.ui_table.rows.clear()
        for i, (source, target) in enumerate(zip(self.decoder.source_words, self.decoder.target_words)):
            self.ui_table.rows.append({'id': i, 'source': source, 'target': target})
        self.ui_table.update()

    def _update_words(self) -> None:
        source_words = [row.get('source') for row in self.ui_table.rows]
        target_words = [row.get('target') for row in self.ui_table.rows]
        self.decoder.source_words = source_words
        self.decoder.target_words = target_words

    def _preload_table(self):
        self.ui_table.rows.clear()
        for i, source in enumerate(self.decoder.source_words):
            self.ui_table.rows.append({'id': i, 'source': source, 'target': ''})
        self.ui_table.update()

    def _split_text(self) -> None:
        _hash = hash(self.decoder.source_text)
        if self.s_hash != _hash:
            self.s_hash = _hash
            self.decoder.split_text()

    async def _decode_words(self) -> None:
        _hash = hash(f'{self.decoder.source_text} {self.decoder.source_language} {self.decoder.target_language}')
        if self.d_hash != _hash:
            self.d_hash = _hash
            # FIXME: strange JavaScript TimeoutError with notification (over ~380 words)
            #   but program seems to work anyway
            notification = ui.notification(
                message = 'decoding',
                position = 'top',
                type = 'ongoing',
                multi_line = True,
                timeout = None,
                spinner = True,
                close_button = False,
            )
            await asyncio.to_thread(self.decoder.decode_words)
            print(len(self.decoder.target_words))
            notification.dismiss()
        self._load_table()

    def _header(self) -> None:
        with ui.header():
            ui.button(text = 'GO BACK TO UPLOAD', on_click = self._open_upload)
            ui.label('DECODING').classes('absolute-center')
            ui.space()
            ui.button(text = 'DICTIONARIES', on_click = self._open_dictionaries)
            ui.button(icon = 'settings', on_click = self._open_settings)

    async def _center(self) -> None:
        self._split_text()
        width = LENF + self.utils.lonlen(self.decoder.source_words) * LENF
        print(width)
        with ui.column().classes('w-full items-center'):
            with ui.card().style('min-width:1000px; min-height:562px'):
                self._table(width)
        self._preload_table()
        await self._decode_words()

    def _table(self, width: int = 150) -> None:
        columns = [
            {'name': 'source', 'field': 'source', 'required': True},
            {'name': 'target', 'field': 'target', 'required': True},
        ]
        self.ui_table = ui.table(columns = columns, rows = [], row_key = 'id') \
            .props('hide-header grid')
        self.ui_table.add_slot(
            'item',
            f'''
            <div class="column" style="width:{width}px" :props="props">
                <div class="col-5">
                    <q-input v-model="props.row.source" dense outlined bg-color=grey-10
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </div>
                <div class="col">
                    <q-input v-model="props.row.target" dense outlined bg-color=blue-grey-10
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)"/>
                </div>
            </div>
            '''
        )
        self.ui_table.on('_upd_row', self._upd_row)

    def _footer(self) -> None:
        with ui.footer():
            ui.button(icon = 'help', on_click = None)
            ui.button(icon = 'save', on_click = self._update_words).classes('absolute-center')
            self.ui_space(width = 500)
            ui.button(text = 'Create PDF', on_click = None)
            ui.space()

    async def page(self) -> None:
        self.__init_ui__()
        await self._center()
        self._header()
        self._footer()
