import re
import math
import chardet
import pathlib
from nicegui import ui, events
from frontend.pages.ui.config import URLS, top_left, bot_left, bot_right
from frontend.pages.ui.error import catch
from frontend.pages.ui.custom import ui_dialog
from frontend.pages.ui.page_abc import Page


class Upload(Page):
    _URL = URLS.UPLOAD

    def __init__(self) -> None:
        super().__init__()
        self._n_words_text: int = 0
        self._pattern = re.compile(r'\S+|\s+')

    @catch
    def _clear_text(self) -> None:
        self.state.title = ''
        self.state.source_text = ''

    @catch
    def _check_source_text(self) -> None:
        word_space_split = re.findall(self._pattern, self.state.source_text)
        n_splits = len(word_space_split)
        self._n_words_text = f'{math.ceil(n_splits / 2)}/{self.word_limit}'
        if n_splits > 2 * self.word_limit:
            self.state.source_text = ''.join(word_space_split[:2 * self.word_limit])
            ui.notify(f'{self.UI_LABELS.UPLOAD.Messages.limit} {self.word_limit} words',
                      type = 'warning', position = 'top')

    def _decode(self) -> None:
        self.state.decode = True

    @catch
    def _upload_handler(self, event: events.UploadEventArguments) -> None:
        try:
            content = event.content.read()
            encoding = chardet.detect(content).get('encoding')
            text = content.decode(encoding)
        except Exception:
            ui.notify(self.UI_LABELS.UPLOAD.Messages.invalid, type = 'warning', position = 'top')
            return
        self.state.title = pathlib.Path(event.name).stem
        self.state.source_text = text
        event.sender.reset()  # noqa upload reset
        # ui.notify(self.UI_LABELS.UPLOAD.Messages.success, type = 'positive', position = 'top')

    @catch
    def _on_upload_reject(self) -> None:
        ui.notify(f'{self.UI_LABELS.UPLOAD.Messages.reject} {self.max_file_size} Bytes',
                  type = 'warning', position = 'top')

    @catch
    def _dialog(self) -> None:
        ui_dialog(label_list = self.UI_LABELS.UPLOAD.Dialogs).open()

    @catch
    def _header(self) -> None:
        with ui.header():
            ui.button(text = self.UI_LABELS.UPLOAD.Header.start_page,
                      on_click = lambda: self.goto(URLS.START))
            ui.label(text = self.UI_LABELS.UPLOAD.Header.upload).classes('absolute-center')
            ui.space()
            ui.button(text = self.UI_LABELS.UPLOAD.Header.decoding,
                      on_click = lambda: self.goto(URLS.DECODING))
            ui.button(text = self.UI_LABELS.UPLOAD.Header.dictionaries,
                      on_click = lambda: self.goto(URLS.DICTIONARIES))
            ui.button(icon = 'settings', on_click = lambda: self.goto(URLS.SETTINGS))

    @catch
    def _center(self) -> None:
        with ui.column().classes('w-full items-center'):
            with ui.card().style('min-width:1000px; min-height:562px; height:85vh') \
                    .classes('w-[50%] items-center'):
                with ui.button(icon = 'help', on_click = self._dialog) \
                        .classes('absolute-top-right'):
                    if self.show_tips: ui.tooltip(self.UI_LABELS.UPLOAD.Tips.help)
                ui.label(self.UI_LABELS.UPLOAD.Uploads[0]).style('font-size:14pt')
                ui.upload(
                    label = self.UI_LABELS.UPLOAD.Uploads[1],
                    on_upload = self._upload_handler,
                    on_rejected = self._on_upload_reject,
                    max_file_size = self.max_file_size,
                    auto_upload = self.auto_upload,
                    max_files = self.max_files) \
                    .props('accept=.txt flat dense')
                with ui.input(label = self.UI_LABELS.UPLOAD.Title).classes(top_left(130, 70)) \
                        .bind_value(self.state, 'title'):
                    if self.show_tips: ui.tooltip(self.UI_LABELS.UPLOAD.Tips.title)
                ui.textarea(
                    label = f'{self.UI_LABELS.UPLOAD.Input_txt[0]} {self.word_limit}',
                    placeholder = self.UI_LABELS.UPLOAD.Input_txt[1],
                    on_change = self._check_source_text) \
                    .style('font-size:12pt') \
                    .classes('w-full h-full flex-grow') \
                    .bind_value(self.state, 'source_text')
                ui.space().style('height:35px')
                self._language_selector()
                self._check_source_text()

    @catch
    def _language_selector(self) -> None:
        languages = self.decoder.get_supported_languages()
        with ui.row().classes(bot_left(10, 10, 'px', '%')):
            ui.select(
                label = self.UI_LABELS.UPLOAD.Footer.source,
                options = ['auto'] + languages) \
                .props('dense options-dense outlined') \
                .style('min-width:200px; font-size:12pt') \
                .bind_value(self.decoder, 'source_language')
            ui.space().style('width:0px')
            ui.select(
                label = self.UI_LABELS.UPLOAD.Footer.target,
                options = languages) \
                .props('dense options-dense outlined') \
                .style('min-width:200px; font-size:12pt') \
                .bind_value(self.decoder, 'target_language')
        with ui.button(text = self.UI_LABELS.UPLOAD.Footer.decode,
                       on_click = lambda: self.goto(URLS.DECODING, call = self._decode)) \
                .classes(bot_right(12, 23, 'px', '%')):
            if self.show_tips: ui.tooltip(self.UI_LABELS.UPLOAD.Tips.decode)
        ui.label().classes(bot_right(30, 10, 'px', '%')).bind_text_from(self, '_n_words_text')
        with ui.button(icon = 'delete', on_click = self._clear_text).classes('absolute-bottom-right'):
            if self.show_tips: ui.tooltip(self.UI_LABELS.UPLOAD.Tips.delete)

    async def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
