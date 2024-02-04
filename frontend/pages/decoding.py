import asyncio
from typing import List
from nicegui import ui
from backend.config.const import URLS
from backend.decoder.pdf import PDF
from frontend.pages.ui_config import LEN, ui_scr_input, ui_tar_input
from frontend.pages.page_abc import Page
import time

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
        self.ui_scr_inputs: List[ui_scr_input] = []
        self.ui_tar_inputs: List[ui_tar_input] = []
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

    def _split_text(self) -> None:
        _hash = hash(self.decoder.source_text)
        if self.s_hash != _hash:
            self.s_hash = _hash
            self.decoder.split_text()

    async def _decode_words(self) -> None:
        _hash = hash(f'{self.decoder.source_text} {self.decoder.source_language} {self.decoder.target_language}')
        if self.d_hash != _hash:
            self.d_hash = _hash
            # FIXME: strange JavaScript TimeoutError with notification (over ~45 words)
            notification = ui.notification(
                message = 'decoding',
                position = 'top',
                type = 'ongoing',
                multi_line = True,
                timeout = None,
                spinner = True,
                # close_button = True,
            )
            await asyncio.to_thread(self.decoder.decode_words)
            notification.dismiss()
            # self.decoder.decode_words = self.decoder.source_text.split()
        self._load_words()

    def _load_words(self) -> None:
        for element, source_word in zip(self.ui_scr_inputs, self.decoder.source_words):
            element.set_value(source_word)
        for element, decode_word in zip(self.ui_tar_inputs, self.decoder.decoded_words):
            element.set_value(decode_word)

    def _update_words(self) -> None:
        self.decoder.source_words = [element.value for element in self.ui_scr_inputs]
        self.decoder.decoded_words = [element.value for element in self.ui_tar_inputs]

    def _header(self) -> None:
        with ui.header().classes('justify-between'):
            ui.button(text = 'GO BACK TO UPLOAD', on_click = self._open_upload)
            ui.label('DECODING').classes('absolute-center')
            ui.space()
            ui.button(text = 'DICTIONARIES', on_click = self._open_dictionaries)
            ui.button(icon = 'settings', on_click = self._open_settings)

    async def _center(self) -> None:
        self._split_text()
        self.ui_scr_inputs.clear()
        self.ui_tar_inputs.clear()
        with ui.column().classes(f'{self.abs_top_center(50)} w-[99%] max-h[90%]').style('align-items: center'):
            with ui.card().style('align-items: center; min-width: 1000px; min-height:500px').classes('max-h[90%]'):
                with ui.row().style('gap: 0rem'):
                    for source_word in self.decoder.source_words:
                        length = len(source_word)
                        length = 5 + 2 * length - LEN * length
                        with ui.column():
                            self.ui_scr_inputs.append(
                                ui_scr_input(value = source_word).props(f'size={length}')
                            )
                            self.ui_tar_inputs.append(
                                ui_tar_input(value = '').props(f'size={length}')
                            )
            self.ui_space(height = 100)
        await self._decode_words()

    def _footer(self) -> None:
        with ui.footer().classes('items-center'):
            ui.button(icon = 'help', on_click = None)
            ui.button(icon = 'save', on_click = self._update_words).classes('absolute-center')
            self.ui_space(width = 500)
            ui.button(text = 'Create PDF', on_click = None)
            ui.space()

    async def page(self) -> None:
        # FIXME UI is extremely unresponsive after reload with a lot of words (over ~200 words)
        self.__init_ui__()
        await self._center()
        self._header()
        self._footer()
