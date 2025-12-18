import pathlib
import asyncio
import traceback
from nicegui import ui, events
from requests.exceptions import ConnectionError as HTTPConnectionError, ProxyError
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.decoder.pdf import PDF
from frontend.pages.ui.error import catch
from frontend.pages.ui.config import URLS, JS, top_right
from frontend.pages.ui.custom import UIGridPages, UIUpload, ui_dialog
from frontend.pages.ui.page_abc import Page


class Decoding(Page):
    __slots__ = (
        '_ui_grid',
        '_ui_menu',
        '_ui_find_input',
        '_ui_repl_input'
    )

    _URL = URLS.DECODING

    def __init__(self) -> None:
        super().__init__()
        self._ui_grid: UIGridPages
        self._ui_menu: ui.menu
        self._ui_find_input: ui.input
        self._ui_repl_input: ui.input

    @catch
    async def _open_pdf_view(self) -> None:
        await self.open_route(
            content = self.state.content,
            file_type = 'pdf',
            filename = self._get_filename(),
            disposition = 'inline'
        )

    @catch
    async def _download_pdf(self) -> None:
        await self.open_route(
            content = self.state.content,
            file_type = 'pdf',
            filename = self._get_filename(),
        )

    def _get_filename(self) -> str:
        return self.state.title if self.state.title else 'decoded'

    @catch
    async def on_key_event(self, event: events.KeyEventArguments):
        if event.modifiers.ctrl and event.key == 'F' and event.action.keydown:
            selected = await self._ui_grid.get_selected()
            if selected: self.state.find = selected
            if hasattr(self, '_ui_menu'):
                self._refresh_replace()
                self._ui_menu.open()

    @catch
    def _refresh_grid(self) -> None:
        if not self.decoder.source_words: return
        self._get_grid_values()
        self._set_grid_values()

    @catch
    def _set_grid_values(self, preload: bool = False, new_source: bool = False,
                         new_indices: bool = False) -> None:
        self._ui_grid.set_values(
            source_words = self.decoder.source_words,
            target_words = self.decoder.target_words,
            preload = preload,
            new_source = new_source,
            new_indices = new_indices
        )

    @catch
    def _get_grid_values(self) -> None:
        self.decoder.source_words, self.decoder.target_words = self._ui_grid.get_values()
        self.state.grid_page = self._ui_grid.get_grid_page()

    @catch
    def _replace_words(self) -> None:
        if not self.decoder.target_words: return
        self._get_grid_values()
        self.decoder.find_replace(
            find = self.state.find,
            repl = self.state.repl
        )
        self._set_grid_values()

    def _clear_replace(self) -> None:
        self.state.find, self.state.repl = '', ''

    @catch
    def _refresh_replace(self) -> None:
        self._ui_find_input.update()
        self._ui_repl_input.update()

    async def _decode_words(self) -> None:
        try:
            if self.decoder.source_text and self.state.decode:
                self.decoder.split_text()
                self._set_grid_values(preload = True, new_source = True)
                notification = ui.notification(
                    message = f'{self.UI_LABELS.DECODING.Messages.decoding} {len(self.decoder.source_words)}',
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
                self.decoder.apply_dict()
                self._set_grid_values()
                notification.dismiss()
            else:
                self._set_grid_values(new_indices = True)
            self.state.decode = False
        except Exception as exception:
            logger.error(f'Error in "_decode_words" with exception: {exception}\n{traceback.format_exc()}')
            ui.notify(self.UI_LABELS.GENERAL.Error.internal, type = 'negative', position = 'top')
            self.state.decode = False

    @catch
    async def _task_handler(self) -> None:
        try:
            self.state.task = asyncio.create_task(asyncio.to_thread(self.decoder.decode_words))
            await self.state.task
            self.state.task = asyncio.create_task(asyncio.to_thread(self.decoder.translate_sentences))
            await self.state.task
            logger.info('Decoding done.')
        except asyncio.exceptions.CancelledError:
            logger.info('Decoding cancelled')
        except ProxyError:
            ui.notify(self.UI_LABELS.SETTINGS.Messages.proxy_error, type = 'warning', position = 'top')
        except HTTPConnectionError:
            ui.notify(self.UI_LABELS.SETTINGS.Messages.connect_error, type = 'warning', position = 'top')
        except DecoderError as exception:
            if exception.code == 429:
                ui.notify(self.UI_LABELS.DECODING.Messages.rate_limit, type = 'warning', position = 'top')
                return
            ui.notify(self.UI_LABELS.GENERAL.Error.internal, type = 'warning', position = 'top')

    @catch
    def _apply_dict(self) -> None:
        if not self.decoder.target_words: return
        self._get_grid_values()
        self.decoder.apply_dict()
        self._set_grid_values()

    @catch
    def create_pdf(self) -> None:
        _hash = hash(f'{self.state.title}{self.settings.pdf_params}'
                     f'{self.decoder.target_words}{self.decoder.source_words}')
        if self.state.c_hash != _hash:
            self.state.c_hash = _hash
            pdf = PDF(**self.settings.pdf_params)
            self.state.content = pdf.convert2pdf(
                title = self.state.title,
                source_words = self.decoder.source_words,
                target_words = self.decoder.target_words
            )

    @catch
    def _on_upload_reject(self) -> None:
        ui.notify(f'{self.UI_LABELS.DECODING.Messages.reject} {self.max_decode_size / 10 ** 3} KB.',
                  type = 'warning', position = 'top')

    @catch
    async def _upload_handler(self, event: events.UploadEventArguments) -> None:
        try:
            data = await event.file.text(encoding = 'utf-8')
            self.decoder.from_json_str(data = data)
            self.state.title = pathlib.Path(event.file.name).stem
            self.decoder.source_text = ' '.join(self.decoder.source_words)
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
        if not self.decoder.sentences: return
        ui_dialog(label_list = self.decoder.sentences[self._ui_grid.slice], max_width = 80, u_width = 'vw').open()

    @catch
    def _pdf_dialog(self) -> None:
        if not self.decoder.target_words: return
        self._get_grid_values()
        self.create_pdf()
        with ui.dialog().style('font-size:12pt') as dialog:
            with ui.card().classes('items-center'):
                ui.button(icon = 'close', on_click = dialog.close) \
                    .classes('absolute-top-right') \
                    .props('dense round size=12px')
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
        if not self.decoder.target_words: return
        self._get_grid_values()
        content = self.decoder.to_json_str()
        await self.open_route(
            content = content,
            file_type = 'json',
            filename = self._get_filename()
        )

    @catch
    def _import(self) -> None:
        with ui.dialog() as dialog:
            with ui.card().classes('items-center').style('font-size:12pt'):
                ui.button(icon = 'close', on_click = dialog.close) \
                    .classes('absolute-top-right') \
                    .props('dense round size=12px')
                ui.label(text = self.UI_LABELS.DECODING.Dialogs_import[0])
                UIUpload(
                    text = self.UI_LABELS.DECODING.Dialogs_import[1],
                    on_upload = self._upload_handler,
                    on_rejected = self._on_upload_reject,
                    max_file_size = self.max_decode_size,
                    auto_upload = self.auto_upload,
                    max_files = self.max_files) \
                    .props('accept=.json')
            dialog.open()

    @catch
    def _replace(self) -> None:
        ui.keyboard(on_key = self.on_key_event, repeating = False, ignore = [])
        with ui.button(icon = 'find_replace', on_click = self._refresh_replace):
            if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.replace)
            with ui.menu().on('show', lambda: ui.run_javascript(JS.FOCUS_INPUT)) as self._ui_menu:
                with ui.menu_item(auto_close = False):
                    self._ui_find_input = ui.input(
                        label = self.UI_LABELS.DECODING.Footer.find,
                        on_change = lambda: self._ui_grid.highlight_text(self.state.find)) \
                        .style('font-size:11pt') \
                        .props('name=find-input') \
                        .bind_value(self.state, 'find')  # props('autofocus')
                with ui.menu_item(auto_close = False):
                    self._ui_repl_input = ui.input(
                        label = self.UI_LABELS.DECODING.Footer.replace) \
                        .style('font-size:11pt') \
                        .bind_value(self.state, 'repl')
                with ui.menu_item(auto_close = False).style('justify-content:center'):
                    with ui.row():
                        ui.button(text = self.UI_LABELS.DECODING.Footer.apply,
                                  on_click = self._replace_words).props('dense')
                        ui.space().style('width:20px')
                        ui.button(icon = 'delete', on_click = self._clear_replace).props('dense')

    @catch
    def _header(self) -> None:
        with ui.header():
            ui.button(text = self.UI_LABELS.DECODING.Header.upload,
                      on_click = lambda: self.goto(URLS.UPLOAD, call = self._get_grid_values))
            ui.label(text = self.UI_LABELS.DECODING.Header.decoding) \
                .classes('absolute-center').style('font-size:14pt')
            ui.space()
            ui.button(text = self.UI_LABELS.DECODING.Header.dictionaries,
                      on_click = lambda: self.goto(URLS.DICTIONARIES, call = self._get_grid_values))
            ui.button(icon = 'settings', on_click = lambda: self.goto(URLS.SETTINGS, call = self._get_grid_values))

    @catch
    async def _center(self) -> None:
        with ui.element().classes('w-full items-center'):
            self._ui_grid = UIGridPages(
                grid_page = self.state.grid_page,
                find_str = self.state.find,
                endofs = self.decoder.regex.endofs,
                quotes = self.decoder.regex.quotes,
            )
            self._ui_grid.page(dark_mode = self.settings.app.dark_mode)
        with ui.footer(): self._ui_grid.pagination()
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
            ui.button(text = self.UI_LABELS.DECODING.Footer.apply_dict, on_click = self._apply_dict)
            ui.space()
            with ui.button(icon = 'refresh', on_click = self._refresh_grid):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.refresh)
            ui.space()
            ui.button(text = self.UI_LABELS.DECODING.Footer.create, on_click = self._pdf_dialog)
            ui.space()
            with ui.button(text = self.UI_LABELS.DECODING.Footer.export, on_click = self._export):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.export)
            ui.space()
            with ui.button(icon = 'reorder', on_click = self._dialog_sentences):
                if self.show_tips: ui.tooltip(self.UI_LABELS.DECODING.Tips.view)

    async def page(self) -> None:
        self.__init_ui__()
        await self._center()
        self._footer()
        self._header()
