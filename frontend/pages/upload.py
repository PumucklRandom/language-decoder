import re
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
        self.pattern = re.compile('\S+|\s+')

    def _clear_text(self) -> None:
        try:
            self.state.title = ''
            self.state.source_text = ''
        except Exception:
            logger.error(f'Error in "_clear_text" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _check_source_text(self) -> None:
        word_space_split = re.findall(self.pattern, self.state.source_text)
        if len(word_space_split) > 2 * self.word_limit:
            self.state.source_text = ''.join(word_space_split[:2 * self.word_limit])
            ui.notify(f'{self.ui_language.UPLOAD.Messages.limit} {self.word_limit} words',
                      type = 'warning', position = 'top')

    def _split_text(self) -> None:
        try:
            if not self.state.source_text:
                # self.state.source_words.clear()
                # self.state.target_words.clear()
                # self.state.sentences.clear()
                return
            self.state.decode = True
            _hash = hash(self.state.source_text)
            if self.state.s_hash == _hash:
                return
            self.state.s_hash = _hash
            self.state.source_words = self.decoder.split_text(source_text = self.state.source_text)
        except Exception:
            logger.error(f'Error in "_split_text" with exception:\n{traceback.format_exc()}')
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
            self._check_source_text()
            event.sender.reset()  # noqa upload reset
            ui.notify(self.ui_language.UPLOAD.Messages.success, type = 'positive', position = 'top')
        except Exception:
            logger.error(f'Error in "_upload_handler" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _on_upload_reject(self) -> None:
        try:
            ui.notify(f'{self.ui_language.UPLOAD.Messages.reject} {self.max_file_size} Bytes',
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
                ui.button(text = self.ui_language.UPLOAD.Header.start_page,
                          on_click = lambda: self.goto(URLS.START))
                ui.label(text = self.ui_language.UPLOAD.Header.upload).classes('absolute-center')
                ui.space()
                ui.button(text = self.ui_language.UPLOAD.Header.decoding,
                          on_click = lambda: self.goto(URLS.DECODING))
                ui.button(text = self.ui_language.UPLOAD.Header.dictionaries,
                          on_click = lambda: self.goto(URLS.DICTIONARIES))
                ui.button(icon = 'settings', on_click = lambda: self.goto(URLS.SETTINGS))
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
                        label = f'{self.ui_language.UPLOAD.Input_txt[0]} {self.word_limit}',
                        placeholder = self.ui_language.UPLOAD.Input_txt[1],
                        on_change = self._check_source_text) \
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
                    options = ['auto'] + languages) \
                    .props('dense options-dense') \
                    .style('min-width:200px; font-size:12pt') \
                    .bind_value(self.state, 'source_language')
                ui.space()
                ui.select(
                    label = self.ui_language.UPLOAD.Footer.target,
                    options = languages) \
                    .props('dense options-dense') \
                    .style('min-width:200px; font-size:12pt') \
                    .bind_value(self.state, 'target_language')
                ui.space().style('width:50px')
                with ui.button(text = self.ui_language.UPLOAD.Footer.decode,
                               on_click = lambda: self.goto(URLS.DECODING, call = self._split_text)):
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
