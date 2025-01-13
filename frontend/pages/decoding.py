import pathlib
import asyncio
import traceback
from nicegui import ui, events, Client
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.decoder.pdf import PDF
from frontend.pages.ui.config import URLS
from frontend.pages.ui.custom import UIGrid, ui_dialog
from frontend.pages.ui.page_abc import Page


class Decoding(Page):
    _URL = URLS.DECODING

    def __init__(self) -> None:
        super().__init__()
        self.ui_grid: UIGrid = None  # noqa
        self.ui_find_input: ui.input = None  # noqa
        self.ui_repl_input: ui.input = None  # noqa
        self.find: str = ''
        self.repl: str = ''
        self.filename: str = 'decoded'
        self.preload: bool = False
        self.task0: asyncio.Task
        self.task1: asyncio.Task

    def _go_to_upload(self) -> None:
        try:
            self._update_words()
            ui.navigate.to(f'{URLS.UPLOAD}')
        except Exception:
            logger.error(f'Error in "_go_to_upload" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _go_to_dictionaries(self) -> None:
        try:
            self._update_words()
            ui.navigate.to(f'{URLS.DICTIONARIES}')
        except Exception:
            logger.error(f'Error in "_go_to_dictionaries" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _go_to_settings(self) -> None:
        try:
            self._update_words()
            ui.navigate.to(f'{URLS.SETTINGS}')
        except Exception:
            logger.error(f'Error in "_go_to_settings" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def _open_pdf_view(self) -> None:
        try:
            await self.open_route(
                content = self.state.content,
                file_type = 'pdf',
                filename = self.filename,
                disposition = 'inline'
            )
        except Exception:
            logger.error(f'Error in "_open_pdf_view" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def _download_pdf(self) -> None:
        try:
            await self.open_route(
                content = self.state.content,
                file_type = 'pdf',
                filename = self.filename
            )
        except Exception:
            logger.error(f'Error in "_download_pdf" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _preload_table(self) -> None:
        try:
            self.preload = True
            self._table.refresh()
            self.preload = False
        except Exception:
            logger.error(f'Error in "_preload_table" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _update_words(self) -> None:
        try:
            self.state.source_words, self.state.target_words = self.ui_grid.get_values()
            self.state.source_words = list(map(str.strip, self.state.source_words))
            self.state.target_words = list(map(str.strip, self.state.target_words))
        except Exception:
            logger.error(f'Error in "_update_words" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _save_words(self) -> None:
        try:
            self._update_words()
            self._table.refresh()
        except Exception:
            logger.error(f'Error in "_save_words" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _replace_words(self) -> None:
        try:
            self._update_words()
            self.state.source_words, self.state.target_words = self.decoder.find_replace(
                source_words = self.state.source_words, target_words = self.state.target_words,
                find = self.find, repl = self.repl
            )
            self._table.refresh()
        except Exception:
            logger.error(f'Error in "_replace_words" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _clear_replace(self) -> None:
        self.find, self.repl = '', ''

    def _refresh_replace(self) -> None:
        try:
            self.ui_find_input.update()
            self.ui_repl_input.update()
        except Exception:
            logger.error(f'Error in "_refresh_replace" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _split_text(self) -> None:
        try:
            self.filename = self.state.title
            _hash = hash(self.state.source_text)
            if self.state.s_hash == _hash:
                return
            self.state.s_hash = _hash
            if not self.state.source_text:
                self.state.source_words.clear()
                self.state.target_words.clear()
                self.state.sentences.clear()
                return
            self.state.source_words = self.decoder.split_text(source_text = self.state.source_text)
        except Exception:
            logger.error(f'Error in "_split_text" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def _decode_words(self) -> None:
        try:
            _hash = hash(f'{self.state.source_text}{self.state.source_language}{self.state.target_language}')
            if self.state.d_hash == _hash:
                self._table.refresh()
                return
            self.state.d_hash = _hash
            if self.state.source_text:
                notification = ui.notification(
                    message = f'{self.ui_language.DECODING.Messages.decoding} {len(self.state.source_words)}',
                    position = 'top',
                    type = 'ongoing',
                    color = 'dark',
                    multi_line = True,
                    timeout = None,
                    spinner = True,
                    close_button = self.ui_language.DECODING.Messages.cancel,
                    on_dismiss = self._task_cancel
                )
                await self._task_handler()
                self._apply_dict()
                notification.dismiss()
        except Exception:
            logger.error(f'Error in "_decode_words" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def _task_handler(self):
        try:
            self.task0 = asyncio.create_task(
                asyncio.to_thread(self.decoder.decode_words, self.state.source_words)
            )
            self.task1 = asyncio.create_task(
                asyncio.to_thread(self.decoder.decode_sentences, self.state.source_words)
            )
            self.state.target_words = await self.task0
            self.state.sentences = await self.task1
        except asyncio.exceptions.CancelledError:
            logger.info('Decoding cancelled')
            self.state.s_hash = 0
            self.state.d_hash = 0
        except Exception:
            logger.error(f'Error in "_task_handler" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _task_cancel(self):
        try:
            self.task0.cancel()
            self.task1.cancel()
        except AttributeError:
            return
        except Exception:
            logger.error(f'Error in "_task_cancel" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _apply_dict(self) -> None:
        try:
            self.state.target_words = self.decoder.apply_dict(
                source_words = self.state.source_words, target_words = self.state.target_words
            )
            self._table.refresh()
        except Exception:
            logger.error(f'Error in "_apply_dict" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def create_pdf(self) -> None:
        try:
            _hash = hash(f'{self.state.title}{self.state.source_words}'
                         f'{self.state.target_words}{self.state.pdf_params}')
            if self.state.c_hash != _hash:
                self.state.c_hash = _hash
                pdf = PDF(**self.state.pdf_params)
                self.state.content = pdf.convert2pdf(
                    title = self.state.title,
                    source_words = self.state.source_words,
                    target_words = self.state.target_words
                )
        except Exception:
            logger.error(f'Error in "create_pdf" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _on_upload_reject(self) -> None:
        try:
            ui.notify(f'{self.ui_language.DECODING.Messages.reject} {self.max_file_size / 10 ** 3} KB',
                      type = 'warning', position = 'top')
        except Exception:
            logger.error(f'Error in "_on_upload_reject" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _upload_handler(self, event: events.UploadEventArguments) -> None:
        try:
            data = event.content.read().decode('utf-8')
            self.state.source_words, self.state.target_words, self.state.sentences = self.decoder.import_(data = data)
            self.state.title = pathlib.Path(event.name).stem
            self.filename = self.state.title
            self.state.source_text = ' '.join(self.state.source_words)
            self.state.s_hash = hash(self.state.source_text)
            self.state.d_hash = hash(
                f'{self.state.source_text}{self.state.source_language}{self.state.target_language}'
            )
            self._table.refresh()
        except DecoderError:
            ui.notify(self.ui_language.DECODING.Messages.invalid, type = 'warning', position = 'top')
        except Exception:
            logger.error(f'Error in "_upload_handler" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')
        finally:
            event.sender.reset()  # noqa upload reset

    def _dialog(self) -> ui_dialog:
        try:
            return ui_dialog(label_list = self.ui_language.DECODING.Dialogs)
        except Exception:
            logger.error(f'Error in "_dialog" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _dialog_sentences(self) -> None:
        try:
            ui_dialog(label_list = self.state.sentences, classes = 'min-w-[80%]', style = 'width:200px').open()
        except Exception:
            logger.error(f'Error in "_dialog_sentences" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _pdf_dialog(self) -> None:
        try:
            if not self.state.target_words:
                return
            self._save_words()
            self.create_pdf()
            with ui.dialog() as dialog:
                with ui.card().classes('items-center'):
                    ui.button(icon = 'close', on_click = dialog.close) \
                        .classes('absolute-top-right') \
                        .props('dense round size=12px')
                    ui.space()
                    ui.label(self.ui_language.DECODING.Dialogs_pdf.text[0])
                    ui.label(self.ui_language.DECODING.Dialogs_pdf.text[1])
                    ui.button(text = self.ui_language.DECODING.Dialogs_pdf.view,
                              on_click = self._open_pdf_view)
                    ui.label(self.ui_language.DECODING.Dialogs_pdf.text[2])
                    ui.button(text = self.ui_language.DECODING.Dialogs_pdf.download,
                              on_click = self._download_pdf)
                    dialog.open()
        except Exception:
            logger.error(f'Error in "_pdf_dialog" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def _export(self) -> None:
        try:
            if not self.state.target_words:
                return
            self._update_words()
            content = self.decoder.export(source_words = self.state.source_words,
                                          target_words = self.state.target_words,
                                          sentences = self.state.sentences)
            await self.open_route(
                content = content,
                file_type = 'json',
                filename = self.filename
            )
        except Exception:
            logger.error(f'Error in "_export" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _import(self) -> None:
        try:
            with ui.dialog() as dialog:
                with ui.card().classes('items-center'):
                    ui.button(icon = 'close', on_click = dialog.close) \
                        .classes('absolute-top-right') \
                        .props('dense round size=12px')
                    ui.label(text = self.ui_language.DECODING.Dialogs_import[0])
                    ui.upload(
                        label = self.ui_language.DECODING.Dialogs_import[1],
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

    def _replace(self):
        try:
            with ui.button(icon = 'find_replace', on_click = self._refresh_replace).props('dense'):
                if self.state.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.replace)
                with ui.menu():
                    # with ui.menu_item(auto_close = False):
                    #     ui.toggle(['source', 'both', 'target'], value = 'both').props('dense')
                    with ui.menu_item(auto_close = False):
                        self.ui_find_input = ui.input(label = 'find').bind_value(self, 'find')
                    with ui.menu_item(auto_close = False):
                        self.ui_repl_input = ui.input(label = 'replace').bind_value(self, 'repl')
                    with ui.menu_item(auto_close = False).style('justify-content:center'):
                        with ui.row():
                            ui.button(text = self.ui_language.DECODING.Footer.replace,
                                      on_click = self._replace_words).props('dense')
                            ui.space().style('width:20px')
                            ui.button(icon = 'delete', on_click = self._clear_replace).props('dense')
        except Exception:
            logger.error(f'Error in "_replace" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _header(self) -> None:
        try:
            with ui.header():
                ui.button(text = self.ui_language.DECODING.Header.go_back, on_click = self._go_to_upload)
                ui.label(text = self.ui_language.DECODING.Header.decoding).classes('absolute-center')
                ui.space()
                ui.button(text = self.ui_language.DECODING.Header.dictionaries, on_click = self._go_to_dictionaries)
                ui.button(icon = 'settings', on_click = self._go_to_settings)
        except Exception:
            logger.error(f'Error in "_header" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def _center(self) -> None:
        try:
            self._split_text()
            with ui.column().classes('w-full items-center'):
                with ui.card().style('min-width:1000px; min-height:562px'):
                    self._table()  # noqa
            self._preload_table()
            await self._decode_words()
            with ui.row().classes('absolute-top-right').style('gap:0.0rem'):
                with ui.column().style('gap:0.0rem'):
                    ui.space().style('height:5px')
                    with ui.button(icon = 'help', on_click = self._dialog().open).props('dense'):
                        if self.state.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.help).style('width:70px')
                ui.space().style('width:5px')
        except Exception:
            logger.error(f'Error in "_center" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    @ui.refreshable
    def _table(self) -> None:
        try:
            self.ui_grid = UIGrid(
                source_words = self.state.source_words,
                target_words = self.state.target_words,
                preload = self.preload,
                dark_mode = self.state.dark_mode
            )
        except Exception:
            logger.error(f'Error in "_open_start_page" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _footer(self) -> None:
        try:
            with ui.footer():
                self._replace()
                ui.space()
                with ui.button(text = self.ui_language.DECODING.Footer.import_, on_click = self._import):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.import_)
                ui.space()
                ui.button(text = self.ui_language.DECODING.Footer.apply, on_click = self._apply_dict)
                ui.space()
                with ui.button(icon = 'save', on_click = self._save_words):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.save)
                ui.space()
                ui.button(text = self.ui_language.DECODING.Footer.create, on_click = self._pdf_dialog)
                ui.space()
                with ui.button(text = self.ui_language.DECODING.Footer.export, on_click = self._export):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.export)
                ui.space()
                with ui.button(icon = 'reorder', on_click = self._dialog_sentences).props('dense'):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.view)
        except Exception:
            logger.error(f'Error in "_footer" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def page(self, client: Client) -> None:
        await self.__init_ui__(client = client)
        self.set_decoder_state()
        await self._center()
        self._header()
        self._footer()
