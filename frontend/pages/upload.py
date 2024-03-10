import pathlib
from nicegui import ui, events
from backend.config.config import URLS, CONFIG
from frontend.pages.ui_custom import ui_dialog, abs_top_left
from frontend.pages.page_abc import Page


class Upload(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.UPLOAD)
        self.ui_uploader: ui.upload = None  # noqa
        self.ui_title: ui.input = None  # noqa
        self.ui_text_box: ui.textarea = None  # noqa
        self.ui_scr_select: ui.select = None  # noqa
        self.ui_tar_select: ui.select = None  # noqa

    def _open_start_page(self) -> None:
        self._update_text()
        self.update_url_history()
        ui.open(f'{URLS.START}')

    def _open_dictionaries(self) -> None:
        self._update_text()
        self.update_url_history()
        ui.open(f'{URLS.DICTIONARIES}')

    def _open_settings(self) -> None:
        self._update_text()
        self.update_url_history()
        ui.open(f'{URLS.SETTINGS}')

    def _open_decoding(self) -> None:
        self._update_text()
        # if self.decoder.source_text:
        self.update_url_history()
        ui.open(f'{URLS.DECODING}')
        # else:
        #     ui.notify(self.ui_language.UPLOAD.Messages.decode,
        #               type = 'warning', position = 'top')

    def _clear_text(self) -> None:
        # self.decoder.title = ''
        self.ui_uploader.reset()
        self.ui_text_box.set_value('')
        self.decoder.source_text = ''
        # self.decoder.source_language = 'auto'
        # self.decoder.target_language = 'english'

    def _load_text(self) -> None:
        self.ui_title.set_value(self.decoder.title)
        self.ui_text_box.set_value(self.decoder.source_text)
        self.ui_scr_select.set_value(self.decoder.source_language)
        self.ui_tar_select.set_value(self.decoder.target_language)

    def _update_text(self) -> None:
        self.decoder.title = self.ui_title.value
        self.decoder.source_text = self.ui_text_box.value
        self.decoder.source_language = self.ui_scr_select.value
        self.decoder.target_language = self.ui_tar_select.value

    def _upload_handler(self, event: events.UploadEventArguments) -> None:
        try:
            text = event.content.read().decode('utf-8')
        except UnicodeDecodeError:
            event.content.seek(0)
            text = event.content.read().decode('utf-16')
        except Exception:
            ui.notify(self.ui_language.UPLOAD.Messages.invalid,
                      type = 'warning', position = 'top')
            return
        self.ui_title.set_value(pathlib.Path(event.name).stem)
        self.ui_text_box.set_value(text)
        event.sender.reset()  # noqa upload reset
        ui.notify(self.ui_language.UPLOAD.Messages.success,
                  type = 'positive', position = 'top')

    def _on_upload_reject(self) -> None:
        ui.notify(f'{self.ui_language.UPLOAD.Messages.reject} {self.max_file_size / 10 ** 3} KB',
                  type = 'warning', position = 'top')

    def _dialog(self) -> ui_dialog:
        return ui_dialog(label_list = self.ui_language.UPLOAD.Dialogs)

    def _header(self) -> None:
        with ui.header():
            ui.button(text = 'START PAGE', on_click = self._open_start_page)
            ui.label('UPLOAD').classes('absolute-center')
            ui.space()
            ui.button(text = 'DICTIONARIES', on_click = self._open_dictionaries)
            ui.button(icon = 'settings', on_click = self._open_settings)

    def _center(self) -> None:
        with ui.column().classes('w-full items-center'):
            with ui.card().classes('w-[50%] items-center') \
                    .style('min-width:1000px; min-height:562px; height:90vh'):
                with ui.button(icon = 'help', on_click = self._dialog().open) \
                        .classes('absolute-top-right'):
                    if self.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.help)
                ui.label(self.ui_language.UPLOAD.Uploads[0]).style('font-size:14pt')
                self.ui_uploader = ui.upload(
                    label = self.ui_language.UPLOAD.Uploads[1],
                    on_upload = self._upload_handler,
                    on_rejected = self._on_upload_reject,
                    max_file_size = self.max_file_size,
                    auto_upload = self.auto_upload,
                    max_files = self.max_files) \
                    .props('accept=.txt flat dense')
                with ui.input(label = self.ui_language.UPLOAD.Title).classes(abs_top_left(130, 160)) as self.ui_title:
                    if self.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.title)
                self.ui_text_box = ui.textarea(
                    label = self.ui_language.UPLOAD.Input_txt[0],
                    placeholder = self.ui_language.UPLOAD.Input_txt[1],
                    on_change = None) \
                    .classes('w-full h-full flex-grow') \
                    .style('min-width:1000px; min-height:562px; font-size:12pt')
                self._language_selector()

    def _language_selector(self) -> None:
        languages = self.decoder.get_supported_languages()
        with ui.row():
            self.ui_scr_select = ui.select(
                label = self.ui_language.UPLOAD.Language[0],
                value = 'auto',
                options = ['auto'] + languages) \
                .props('dense options-dense') \
                .style('min-width:200px; font-size:12pt')
            ui.space()
            self.ui_tar_select = ui.select(
                label = self.ui_language.UPLOAD.Language[1],
                value = 'english',
                options = languages) \
                .props('dense options-dense') \
                .style('min-width:200px; font-size:12pt')
            ui.space()
            with ui.button(icon = 'save', on_click = self._update_text):
                if self.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.save)
            ui.space()
            with ui.button(text = 'DECODE', on_click = self._open_decoding):
                if self.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.decode)
            with ui.button(icon = 'delete', on_click = self._clear_text) \
                    .classes('absolute-bottom-right'):
                if self.show_tips: ui.tooltip(self.ui_language.UPLOAD.Tips.delete)
            ui.space().style('width:100px')
            self._load_text()

    def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
