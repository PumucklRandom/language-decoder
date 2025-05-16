import pathlib
import asyncio
import traceback
from nicegui import ui, events, Client
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.decoder.pdf import PDF
from frontend.pages.ui.config import URLS
from frontend.pages.ui.custom import UIGridPages, ui_dialog
from frontend.pages.ui.page_abc import Page


class Decoding(Page):
    _URL = URLS.DECODING

    def __init__(self) -> None:
        super().__init__()
        self.filename: str = 'decoded'
        self.task: asyncio.Task
        self.ui_grid: UIGridPages
        self.ui_find_input: ui.input
        self.ui_repl_input: ui.input

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

    def _refresh_grid(self) -> None:
        try:
            self._update_words()
            self._update_grid()
        except Exception:
            logger.error(f'Error in "_refresh_grid" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _update_grid(self, preload: bool = False, new_source: bool = False, new_indices: bool = False) -> None:
        try:
            self.ui_grid.set_values(
                source_words = self.state.source_words,
                target_words = self.state.target_words,
                preload = preload,
                new_source = new_source,
                new_indices = new_indices
            )
        except Exception:
            logger.error(f'Error in "_update_grid" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _update_words(self) -> None:
        try:
            self.state.source_words, self.state.target_words = self.ui_grid.get_values()
            self.state.grid_page = self.ui_grid.get_grid_page()
        except Exception:
            logger.error(f'Error in "_update_words" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _replace_words(self) -> None:
        try:
            self._update_words()
            self.state.source_words, self.state.target_words = self.decoder.find_replace(
                source_words = self.state.source_words,
                target_words = self.state.target_words,
                find = self.state.find,
                repl = self.state.repl
            )
            self._update_grid()
        except Exception:
            logger.error(f'Error in "_replace_words" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _clear_replace(self) -> None:
        self.state.find, self.state.repl = '', ''

    def _refresh_replace(self) -> None:
        try:
            self.ui_find_input.update()
            self.ui_repl_input.update()
        except Exception:
            logger.error(f'Error in "_refresh_replace" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def _decode_words(self) -> None:
        try:
            if self.state.title: self.filename = self.state.title
            if self.state.source_text and self.state.decode:
                self.state.source_words = self.decoder.split_text(source_text = self.state.source_text)
                self._update_grid(preload = True, new_source = True)
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
                notification.dismiss()
            else:
                self._update_grid(new_indices = True)
            self.state.decode = False
        except Exception:
            logger.error(f'Error in "_decode_words" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def _task_handler(self) -> None:
        try:
            self.task = asyncio.create_task(asyncio.to_thread(
                self.decoder.decode_words,
                source_words = self.state.source_words
            ))
            self.state.target_words = await self.task
            self.task = asyncio.create_task(asyncio.to_thread(
                self.decoder.translate_sentences,
                source_words = self.state.source_words
            ))
            self.state.sentences = await self.task
            self._apply_dict()
            logger.info('Decoding done.')
        except asyncio.exceptions.CancelledError:
            logger.info('Decoding cancelled')
        except Exception:
            logger.error(f'Error in "_task_handler" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _task_cancel(self) -> None:
        try:
            self.task.cancel()
        except AttributeError:
            return
        except Exception:
            logger.error(f'Error in "_task_cancel" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _apply_dict(self) -> None:
        try:
            self.state.target_words = self.decoder.apply_dict(
                source_words = self.state.source_words,
                target_words = self.state.target_words,
                dict_name = self.state.dict_name
            )
            self._update_grid()
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
            self.state.source_words, self.state.target_words, self.state.sentences = self.decoder.from_json_str(
                data = data
            )
            self.state.title = pathlib.Path(event.name).stem
            self.filename = self.state.title
            self.state.source_text = ' '.join(self.state.source_words)
            self._update_grid(new_source = True)
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
            if not self.state.target_words: return
            self._update_words()
            self.create_pdf()
            with ui.dialog() as dialog:
                with ui.card().classes('items-center'):
                    ui.button(icon = 'close', on_click = dialog.close) \
                        .props('dense round size=12px') \
                        .classes('absolute-top-right')
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
            if not self.state.target_words: return
            self._update_words()
            content = self.decoder.to_json_str(
                source_words = self.state.source_words,
                target_words = self.state.target_words,
                sentences = self.state.sentences
            )
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
                        .props('dense round size=12px') \
                        .classes('absolute-top-right')
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

    def _replace(self) -> None:
        try:
            with ui.button(icon = 'find_replace', on_click = self._refresh_replace).props('dense'):
                if self.state.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.replace)
                with ui.menu():
                    with ui.menu_item(auto_close = False):
                        # TODO: add highlighting of matches while typing
                        self.ui_find_input = ui.input(label = 'find').bind_value(self.state, 'find')
                    with ui.menu_item(auto_close = False):
                        self.ui_repl_input = ui.input(label = 'replace').bind_value(self.state, 'repl')
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
                ui.button(text = self.ui_language.DECODING.Header.upload,
                          on_click = lambda: self.goto(URLS.UPLOAD, call = self._update_words))
                ui.label(text = self.ui_language.DECODING.Header.decoding).classes('absolute-center')
                ui.space()
                ui.button(text = self.ui_language.DECODING.Header.dictionaries,
                          on_click = lambda: self.goto(URLS.DICTIONARIES, call = self._update_words))
                ui.button(icon = 'settings', on_click = lambda: self.goto(URLS.SETTINGS, call = self._update_words))
        except Exception:
            logger.error(f'Error in "_header" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def _center(self) -> None:
        try:
            with ui.element().classes('w-full items-center'):
                self.ui_grid = UIGridPages(
                    grid_page = self.state.grid_page,
                    endofs = self.decoder.regex.endofs + self.decoder.regex.quotes,
                    dark_mode = self.state.dark_mode,
                )
                self.ui_grid()
            await self._decode_words()
            with ui.row().style('gap:0.0rem').classes('absolute-top-right'):
                with ui.column().style('gap:0.0rem'):
                    ui.space().style('height:5px')
                    with ui.button(icon = 'help', on_click = self._dialog().open).props('dense'):
                        if self.state.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.help).style('width:70px')
                ui.space().style('width:5px')
        except Exception:
            logger.error(f'Error in "_center" with exception:\n{traceback.format_exc()}')
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
                with ui.button(icon = 'refresh', on_click = self._refresh_grid):
                    if self.state.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.refresh)
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
