import re
import math
import chardet
import pathlib
from re import Pattern
from nicegui import ui, events
from frontend.pages.ui.error import catch
from frontend.pages.ui.config import URLS, top_left, bot_left, bot_right
from frontend.pages.ui.custom import UIUpload, ui_dialog
from frontend.pages.ui.page_abc import Page


class Upload(Page):
    __slots__ = (
        '_pattern',
        '_counter_label'
    )

    _URL = URLS.UPLOAD

    def __init__(self) -> None:
        super().__init__()
        self._pattern: Pattern = re.compile(r'\S+|\s+')
        self._counter_label: str = f'0/{self.word_limit}'

    @catch
    def _clear_text(self) -> None:
        self.state.title = ''
        self.decoder.source_text = ''

    @catch
    def _check_source_text(self) -> None:
        word_space_split = re.findall(self._pattern, self.decoder.source_text)
        n_words = math.ceil(len(word_space_split) / 2)
        if n_words <= self.word_limit:
            self._counter_label = f'{n_words}/{self.word_limit}'
            return
        self._counter_label = f'{self.word_limit}/{self.word_limit}'
        self.decoder.source_text = ''.join(word_space_split[:2 * self.word_limit])
        ui.notify(
            f'{self.UI_LABELS.UPLOAD.Messages.limit[0]} {self.word_limit} {self.UI_LABELS.UPLOAD.Messages.limit[1]}',
            type = 'warning', position = 'top'
        )

    def _decode(self) -> None:
        self.state.decode = True

    @catch
    def _on_upload_reject(self) -> None:
        ui.notify(f'{self.UI_LABELS.UPLOAD.Messages.reject} {self.max_file_size / 10 ** 3} KB.',
                  type = 'warning', position = 'top')

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
        self.decoder.source_text = text
        event.sender.reset()  # noqa upload reset
        # ui.notify(self.UI_LABELS.UPLOAD.Messages.success, type = 'positive', position = 'top')

    @catch
    def _dialog(self) -> None:
        ui_dialog(label_list = self.UI_LABELS.UPLOAD.Dialogs).open()

    @catch
    def _header(self) -> None:
        with ui.header():
            ui.button(text = self.UI_LABELS.UPLOAD.Header.start_page,
                      on_click = lambda: self.goto(URLS.START))
            ui.label(text = self.UI_LABELS.UPLOAD.Header.upload) \
                .classes('absolute-center').style('font-size:14pt')

            ui.space()
            ui.button(text = self.UI_LABELS.UPLOAD.Header.decoding,
                      on_click = lambda: self.goto(URLS.DECODING))
            ui.button(text = self.UI_LABELS.UPLOAD.Header.dictionaries,
                      on_click = lambda: self.goto(URLS.DICTIONARIES))
            ui.button(icon = 'settings', on_click = lambda: self.goto(URLS.SETTINGS))

    @catch
    def _center(self) -> None:
        with ui.column().classes('w-full items-center'):
            with ui.card().classes('w-[50%] items-center') \
                    .style('min-width:1000px; min-height:562px; height:85vh'):
                with ui.button(icon = 'help', on_click = self._dialog) \
                        .classes('absolute-top-right'):
                    if self.show_tips: ui.tooltip(self.UI_LABELS.UPLOAD.Tips.help)
                ui.label(self.UI_LABELS.UPLOAD.Uploads[0]).style('font-size:13pt')
                UIUpload(
                    text = self.UI_LABELS.UPLOAD.Uploads[1],
                    on_upload = self._upload_handler,
                    on_rejected = self._on_upload_reject,
                    max_file_size = self.max_file_size,
                    auto_upload = self.auto_upload,
                    max_files = self.max_files) \
                    .props('accept=.txt')
                with ui.input(label = self.UI_LABELS.UPLOAD.Title).classes(top_left(130, 70)) \
                        .style('width:205px; font-size:12pt').bind_value(self.state, 'title'):
                    if self.show_tips: ui.tooltip(self.UI_LABELS.UPLOAD.Tips.title)
                ui.textarea(
                    label = f'{self.UI_LABELS.UPLOAD.Input_txt[0]}',
                    placeholder = self.UI_LABELS.UPLOAD.Input_txt[1],
                    on_change = self._check_source_text) \
                    .classes('w-full h-full flex-grow') \
                    .style('font-size:12pt') \
                    .bind_value(self.decoder, 'source_text')
                ui.space().style('height:35px')
                self._language_selector()

    @catch
    def _language_selector(self) -> None:
        languages = self.decoder.get_supported_languages()
        with ui.row().classes(bot_left(10, 10, 'px', '%')):
            ui.select(
                label = self.UI_LABELS.UPLOAD.Footer.source,
                options = ['auto'] + languages) \
                .style('min-width:200px; font-size:12pt') \
                .props('dense options-dense outlined popup-content-style="font-size: 11pt"') \
                .bind_value(self.decoder, 'source_language')
            ui.space().style('width:0px')
            ui.select(
                label = self.UI_LABELS.UPLOAD.Footer.target,
                options = languages) \
                .style('min-width:200px; font-size:12pt') \
                .props('dense options-dense outlined popup-content-style="font-size: 11pt"') \
                .bind_value(self.decoder, 'target_language')
        with ui.button(text = self.UI_LABELS.UPLOAD.Footer.decode,
                       on_click = lambda: self.goto(URLS.DECODING, call = self._decode)) \
                .classes(bot_right(12, 23, 'px', '%')):
            if self.show_tips: ui.tooltip(self.UI_LABELS.UPLOAD.Tips.decode)
        ui.label().classes(bot_right(30, 10, 'px', '%')) \
            .style('font-size:11pt').bind_text_from(self, '_counter_label')
        with ui.button(icon = 'delete', on_click = self._clear_text).classes('absolute-bottom-right'):
            if self.show_tips: ui.tooltip(self.UI_LABELS.UPLOAD.Tips.delete)

    async def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
