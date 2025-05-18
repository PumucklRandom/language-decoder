import re
import math
import pathlib
import traceback
from nicegui import ui, events, Client
from backend.logger.logger import logger
from frontend.pages.ui.config import URLS
from frontend.pages.ui.custom import ui_dialog, top_left, bot_left, bot_right
from frontend.pages.ui.page_abc import Page


class Upload(Page):
    _URL = URLS.UPLOAD

    def __init__(self) -> None:
        super().__init__()
        self.n_word_text: int = 0
        self.pattern = re.compile(r'\S+|\s+')

    def _clear_text(self) -> None:
        try:
            self.state.title = ''
            self.state.source_text = ''
        except Exception:
            logger.error(f'Error in "_clear_text" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _check_source_text(self) -> None:
        word_space_split = re.findall(self.pattern, self.state.source_text)
        n_split = len(word_space_split)
        self.n_word_text = f'{math.ceil(n_split / 2)}/{self.word_limit}'
        if n_split > 2 * self.word_limit:
            self.state.source_text = ''.join(word_space_split[:2 * self.word_limit])
            ui.notify(f'{self.ui_language.UPLOAD.Messages.limit} {self.word_limit} words',
                      type = 'warning', position = 'top')

    def _decode(self) -> None:
        try:
            self.state.decode = True
        except Exception:
            logger.error(f'Error in "_decode" with exception:\n{traceback.format_exc()}')
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
                with ui.card().style('min-width:1000px; min-height:562px; height:85vh') \
                        .classes('w-[50%] items-center'):
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
                    with ui.input(label = self.ui_language.UPLOAD.Title).classes(top_left(130, 70)) \
                            .bind_value(self.state, 'title'):
                        if self.state.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.title)
                    ui.textarea(
                        label = f'{self.ui_language.UPLOAD.Input_txt[0]} {self.word_limit}',
                        placeholder = self.ui_language.UPLOAD.Input_txt[1],
                        on_change = self._check_source_text) \
                        .style('font-size:12pt') \
                        .classes('w-full h-full flex-grow') \
                        .bind_value(self.state, 'source_text')
                    ui.space().style('height:35px')
                    self._language_selector()
                    self._check_source_text()
        except Exception:
            logger.error(f'Error in "_center" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _language_selector(self) -> None:
        try:
            languages = self.decoder.get_supported_languages()
            with ui.row().classes(bot_left(10, 10, 'px', '%')):
                ui.select(
                    label = self.ui_language.UPLOAD.Footer.source,
                    options = ['auto'] + languages) \
                    .props('dense options-dense outlined') \
                    .style('min-width:200px; font-size:12pt') \
                    .bind_value(self.state, 'source_language')
                ui.space().style('width:0px')
                ui.select(
                    label = self.ui_language.UPLOAD.Footer.target,
                    options = languages) \
                    .props('dense options-dense outlined') \
                    .style('min-width:200px; font-size:12pt') \
                    .bind_value(self.state, 'target_language')
            with ui.button(text = self.ui_language.UPLOAD.Footer.decode,
                           on_click = lambda: self.goto(URLS.DECODING, call = self._decode)) \
                    .classes(bot_right(12, 20, 'px', '%')):
                if self.state.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.decode)
            ui.label().classes(bot_right(30, 10, 'px', '%')).bind_text_from(self, 'n_word_text')
            with ui.button(icon = 'delete', on_click = self._clear_text).classes('absolute-bottom-right'):
                if self.state.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.delete)
        except Exception:
            logger.error(f'Error in "_language_selector" with exception:\n{traceback.format_exc()}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    async def page(self, client: Client) -> None:
        await self.__init_ui__(client = client)
        self._header()
        self._center()
