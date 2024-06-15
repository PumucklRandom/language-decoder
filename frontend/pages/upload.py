import pathlib
import traceback
from nicegui import ui, events, Client
from backend.logger.logger import logger
from frontend.pages.ui.config import URLS
from frontend.pages.ui.custom import ui_dialog, abs_top_left
from frontend.pages.ui.page_abc import Page


class Upload(Page):
    _URL = URLS.UPLOAD

    def __init__(self) -> None:
        super().__init__()

    def _open_start_page(self) -> None:
        try:
            self.update_url_history()
            ui.open(f'{URLS.START}')
        except Exception:
            logger.error(f'Error in "_open_start_page" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _open_dictionaries(self) -> None:
        try:
            self.update_url_history()
            ui.open(f'{URLS.DICTIONARIES}')
        except Exception:
            logger.error(f'Error in "_open_dictionaries" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _open_settings(self) -> None:
        try:
            self.update_url_history()
            ui.open(f'{URLS.SETTINGS}')
        except Exception:
            logger.error(f'Error in "_open_settings" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _open_decoding(self) -> None:
        try:
            self.update_url_history()
            ui.open(f'{URLS.DECODING}')
        except Exception:
            logger.error(f'Error in "_open_decoding" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _clear_text(self) -> None:
        try:
            self.state.title = ''
            self.state.source_text = ''
            # self.state.source_language = 'auto'
            # self.state.target_language = 'english'
        except Exception:
            logger.error(f'Error in "_clear_text" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _upload_handler(self, event: events.UploadEventArguments) -> None:
        try:
            text = event.content.read().decode('utf-8')
        except UnicodeDecodeError:
            event.content.seek(0)
            text = event.content.read().decode('utf-16')
        except Exception:
            ui.notify(self.ui_language.UPLOAD.Messages.invalid, type = 'warning', position = 'top')
            return
        try:
            self.state.title = pathlib.Path(event.name).stem
            self.state.source_text = text
            event.sender.reset()  # noqa upload reset
            ui.notify(self.ui_language.UPLOAD.Messages.success, type = 'positive', position = 'top')
        except Exception:
            logger.error(f'Error in "_upload_handler" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _on_upload_reject(self) -> None:
        try:
            ui.notify(f'{self.ui_language.UPLOAD.Messages.reject} {self.max_file_size / 10 ** 3} KB',
                      type = 'warning', position = 'top')
        except Exception:
            logger.error(f'Error in "_on_upload_reject" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _dialog(self) -> ui_dialog:
        try:
            return ui_dialog(label_list = self.ui_language.UPLOAD.Dialogs)
        except Exception:
            logger.error(f'Error in "_dialog" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _header(self) -> None:
        try:
            with ui.header():
                ui.button(text = self.ui_language.UPLOAD.Header.start_page, on_click = self._open_start_page)
                ui.label(text = self.ui_language.UPLOAD.Header.upload).classes('absolute-center')
                ui.space()
                ui.button(text = self.ui_language.UPLOAD.Header.dictionaries, on_click = self._open_dictionaries)
                ui.button(icon = 'settings', on_click = self._open_settings)
        except Exception:
            logger.error(f'Error in "_header" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _center(self) -> None:
        try:
            with ui.column().classes('w-full items-center'):
                with ui.card().classes('w-[50%] items-center') \
                        .style('min-width:1000px; min-height:562px; height:85vh'):
                    with ui.button(icon = 'help', on_click = self._dialog().open) \
                            .classes('absolute-top-right'):
                        if self.state.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.help)
                    ui.label(self.ui_language.UPLOAD.Uploads[0]).style('font-size:14pt')
                    ui.upload(
                        label = self.ui_language.UPLOAD.Uploads[1],
                        on_upload = self._upload_handler,
                        on_rejected = self._on_upload_reject,
                        max_file_size = self.max_file_size,
                        auto_upload = self.auto_upload,
                        max_files = self.max_files) \
                        .props('accept=.txt flat dense')
                    with ui.input(label = self.ui_language.UPLOAD.Title) \
                            .classes(abs_top_left(130, 160)) \
                            .bind_value(self.state, 'title'):
                        if self.state.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.title)
                    ui.textarea(
                        label = self.ui_language.UPLOAD.Input_txt[0],
                        placeholder = self.ui_language.UPLOAD.Input_txt[1],
                        on_change = None) \
                        .classes('w-full h-full flex-grow') \
                        .style('font-size:12pt') \
                        .bind_value(self.state, 'source_text')
                    self._language_selector()
        except Exception:
            logger.error(f'Error in "_center" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _language_selector(self) -> None:
        try:
            languages = self.decoder.get_supported_languages()
            with ui.row():
                ui.select(
                    label = self.ui_language.UPLOAD.Footer.source,
                    # value = 'auto',
                    options = ['auto'] + languages) \
                    .props('dense options-dense') \
                    .style('min-width:200px; font-size:12pt') \
                    .bind_value(self.state, 'source_language')
                ui.space()
                ui.select(
                    label = self.ui_language.UPLOAD.Footer.target,
                    # value = 'english',
                    options = languages) \
                    .props('dense options-dense') \
                    .style('min-width:200px; font-size:12pt') \
                    .bind_value(self.state, 'target_language')
                ui.space()
                # with ui.button(icon = 'save', on_click = self._update_text):
                #     if self.state.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.save)
                ui.space()
                with ui.button(text = self.ui_language.UPLOAD.Footer.decode, on_click = self._open_decoding):
                    if self.state.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.decode)
                with ui.button(icon = 'delete', on_click = self._clear_text) \
                        .classes('absolute-bottom-right'):
                    if self.state.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.delete)
                ui.space().style('width:100px')
        except Exception:
            logger.error(f'Error in "_language_selector" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def page(self, client: Client) -> None:
        await self.__init_ui__(client = client)
        self._header()
        self._center()
