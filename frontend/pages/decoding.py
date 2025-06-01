import pathlib
import asyncio
from nicegui import ui, events, Client
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.decoder.pdf import PDF
from frontend.pages.ui.config import URLS, JS, top_right
from frontend.pages.ui.error import catch
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

    @catch
    async def _open_pdf_view(self) -> None:
        await self.open_route(
            content = self.state.content,
            file_type = 'pdf',
            filename = self.filename,
            disposition = 'inline'
        )

    @catch
    async def _download_pdf(self) -> None:
        await self.open_route(
            content = self.state.content,
            file_type = 'pdf',
            filename = self.filename
        )

    @catch
    def _refresh_grid(self) -> None:
        self._get_grid_values()
        self._set_grid_values()

    @catch
    def _set_grid_values(self, preload: bool = False, new_source: bool = False,
                         new_indices: bool = False) -> None:
        self.ui_grid.set_values(
            source_words = self.state.source_words,
            target_words = self.state.target_words,
            preload = preload,
            new_source = new_source,
            new_indices = new_indices
        )

    @catch
    def _get_grid_values(self) -> None:
        self.state.source_words, self.state.target_words = self.ui_grid.get_values()
        self.state.grid_page = self.ui_grid.get_grid_page()

    @catch
    def _replace_words(self) -> None:
        self._get_grid_values()
        self.state.source_words, self.state.target_words = self.decoder.find_replace(
            source_words = self.state.source_words,
            target_words = self.state.target_words,
            find = self.state.find,
            repl = self.state.repl
        )
        self._set_grid_values()

    def _clear_replace(self) -> None:
        self.state.find, self.state.repl = '', ''

    @catch
    def _refresh_replace(self) -> None:
        self.ui_find_input.update()
        self.ui_repl_input.update()

    @catch
    async def _decode_words(self) -> None:
        if self.state.title: self.filename = self.state.title
        if self.state.source_text and self.state.decode:
            self.state.source_words = self.decoder.split_text(source_text = self.state.source_text)
            self._set_grid_values(preload = True, new_source = True)
            notification = ui.notification(
                message = f'{self.UI_LABELS.DECODING.Messages.decoding} {len(self.state.source_words)}',
                position = 'top',
                type = 'ongoing',
                color = 'dark',
                multi_line = True,
                timeout = None,
                spinner = True,
                close_button = self.UI_LABELS.DECODING.Messages.cancel,
                on_dismiss = self._task_cancel
            )
            await self._task_handler()
            notification.dismiss()
        else:
            self._set_grid_values(new_indices = True)
        self.state.decode = False

    @catch
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
        except DecoderError as exception:
            logger.warning(exception.message)
            if exception.code == 429:
                ui.notify(self.UI_LABELS.DECODING.Messages.rate_limit, type = 'warning', position = 'top')

    @catch
    def _task_cancel(self) -> None:
        try:
            self.task.cancel()
        except AttributeError:
            return

    @catch
    def _apply_dict(self) -> None:
        self.state.target_words = self.decoder.apply_dict(
            source_words = self.state.source_words,
            target_words = self.state.target_words,
        )
        self._set_grid_values()

    @catch
    def create_pdf(self) -> None:
        _hash = hash(f'{self.state.title}{self.settings.pdf_params}'
                     f'{self.state.target_words}{self.state.source_words}')
        if self.state.c_hash != _hash:
            self.state.c_hash = _hash
            pdf = PDF(**self.settings.pdf_params)
            self.state.content = pdf.convert2pdf(
                title = self.state.title,
                source_words = self.state.source_words,
                target_words = self.state.target_words
            )

    @catch
    def _on_upload_reject(self) -> None:
        ui.notify(f'{self.UI_LABELS.DECODING.Messages.reject} {self.max_decode_size / 10 ** 3} KB',
                  type = 'warning', position = 'top')

    @catch
    def _upload_handler(self, event: events.UploadEventArguments) -> None:
        try:
            data = event.content.read().decode('utf-8')
            self.state.source_words, self.state.target_words, self.state.sentences = self.decoder.from_json_str(
                data = data
            )
            self.state.title = pathlib.Path(event.name).stem
            self.filename = self.state.title
            self.state.source_text = ' '.join(self.state.source_words)
            self._set_grid_values(new_source = True)
        except DecoderError:
            ui.notify(self.UI_LABELS.DECODING.Messages.invalid, type = 'warning', position = 'top')
        finally:
            event.sender.reset()  # noqa upload reset

    @catch
    def _dialog(self) -> None:
        ui_dialog(label_list = self.UI_LABELS.DECODING.Dialogs).open()

    @catch
    def _dialog_sentences(self) -> None:
        ui_dialog(label_list = self.state.sentences, classes = 'min-w-[80%]', style = 'width:200px').open()

    @catch
    def _pdf_dialog(self) -> None:
        if not self.state.target_words: return
        self._get_grid_values()
        self.create_pdf()
        with ui.dialog() as dialog:
            with ui.card().classes('items-center'):
                ui.button(icon = 'close', on_click = dialog.close) \
                    .props('dense round size=12px') \
                    .classes('absolute-top-right')
                ui.space()
                ui.label(self.UI_LABELS.DECODING.Dialogs_pdf.text[0])
                ui.label(self.UI_LABELS.DECODING.Dialogs_pdf.text[1])
                ui.button(text = self.UI_LABELS.DECODING.Dialogs_pdf.view,
                          on_click = self._open_pdf_view)
                ui.label(self.UI_LABELS.DECODING.Dialogs_pdf.text[2])
                ui.button(text = self.UI_LABELS.DECODING.Dialogs_pdf.download,
                          on_click = self._download_pdf)
                dialog.open()

    @catch
    async def _export(self) -> None:
        if not self.state.target_words: return
        self._get_grid_values()
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

    @catch
    def _import(self) -> None:
        with ui.dialog() as dialog:
            with ui.card().classes('items-center'):
                ui.button(icon = 'close', on_click = dialog.close) \
                    .props('dense round size=12px') \
                    .classes('absolute-top-right')
                ui.label(text = self.UI_LABELS.DECODING.Dialogs_import[0])
                ui.upload(
                    label = self.UI_LABELS.DECODING.Dialogs_import[1],
                    on_upload = self._upload_handler,
                    on_rejected = self._on_upload_reject,
                    max_file_size = self.max_decode_size,
                    auto_upload = self.auto_upload,
                    max_files = self.max_files) \
                    .props('accept=.json flat dense')
            dialog.open()

    @catch
    def _replace(self) -> None:
        with ui.button(icon = 'find_replace', on_click = self._refresh_replace).props('dense'):
            if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.replace)
            with ui.menu().on('show', lambda: ui.run_javascript(JS.FOCUS_INPUT)):
                with ui.menu_item(auto_close = False):
                    self.ui_find_input = ui.input(
                        label = 'find',
                        on_change = lambda: self.ui_grid.highlight_text(self.state.find)
                    ).bind_value(self.state, 'find')
                with ui.menu_item(auto_close = False):
                    self.ui_repl_input = ui.input(label = 'replace').bind_value(self.state, 'repl')
                with ui.menu_item(auto_close = False).style('justify-content:center'):
                    with ui.row():
                        ui.button(text = self.UI_LABELS.DECODING.Footer.replace,
                                  on_click = self._replace_words).props('dense')
                        ui.space().style('width:20px')
                        ui.button(icon = 'delete', on_click = self._clear_replace).props('dense')

    @catch
    def _header(self) -> None:
        with ui.header():
            ui.button(text = self.UI_LABELS.DECODING.Header.upload,
                      on_click = lambda: self.goto(URLS.UPLOAD, call = self._get_grid_values))
            ui.label(text = self.UI_LABELS.DECODING.Header.decoding).classes('absolute-center')
            ui.space()
            ui.button(text = self.UI_LABELS.DECODING.Header.dictionaries,
                      on_click = lambda: self.goto(URLS.DICTIONARIES, call = self._get_grid_values))
            ui.button(icon = 'settings', on_click = lambda: self.goto(URLS.SETTINGS, call = self._get_grid_values))

    @catch
    async def _center(self) -> None:
        with ui.element().classes('w-full items-center'):
            self.ui_grid = UIGridPages(
                grid_page = self.state.grid_page,
                endofs = self.decoder.regex.endofs + self.decoder.regex.quotes,
                find_str = self.state.find
            )
            self.ui_grid.page(dark_mode = self.settings.app.dark_mode)
        with ui.footer(): self.ui_grid.pagination()
        await self._decode_words()
        with ui.button(icon = 'help', on_click = self._dialog) \
                .classes(top_right(5, 5)).props('dense'):
            if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.help).style('width:70px')

    @catch
    def _footer(self) -> None:
        with ui.footer():
            self._replace()
            ui.space()
            with ui.button(text = self.UI_LABELS.DECODING.Footer.import_, on_click = self._import):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.import_)
            ui.space()
            ui.button(text = self.UI_LABELS.DECODING.Footer.apply, on_click = self._apply_dict)
            ui.space()
            with ui.button(icon = 'refresh', on_click = self._refresh_grid):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.refresh)
            ui.space()
            ui.button(text = self.UI_LABELS.DECODING.Footer.create, on_click = self._pdf_dialog)
            ui.space()
            with ui.button(text = self.UI_LABELS.DECODING.Footer.export, on_click = self._export):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.export)
            ui.space()
            with ui.button(icon = 'reorder', on_click = self._dialog_sentences).props('dense'):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.view)

    async def page(self, client: Client) -> None:
        await self.__init_ui__(client = client)
        await self._center()
        self._footer()
        self._header()
