from nicegui import ui, events
from backend.config.const import URLS
from frontend.pages.page_abc import Page


class Upload(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.UPLOAD)
        self.ui_uploader: ui.upload = None
        self.ui_text_box: ui.textarea = None
        self.ui_scr_select: ui.select = None
        self.ui_tar_select: ui.select = None
        self.max_file_size: int = 10 ** 5
        self.auto_upload: bool = False
        self.max_files: int = 1

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
        if self.decoder.source_text:
            self.update_url_history()
            ui.open(f'{URLS.DECODING}')
        else:
            self._source_text_mis_notify()

    def _clear_text(self) -> None:
        self.ui_uploader.reset()
        self.ui_text_box.set_value(None)
        self.decoder.source_text = None
        # self.decoder.source_language = 'auto'
        # self.decoder.target_language = 'english'

    def _load_text(self) -> None:
        self.ui_text_box.set_value(self.decoder.source_text)
        self.ui_scr_select.set_value(self.decoder.source_language)
        self.ui_tar_select.set_value(self.decoder.target_language)

    def _update_text(self) -> None:
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
            self._upload_error_notify()
            return
        self.ui_text_box.set_value(text)
        event.sender.reset()  # noqa upload reset
        ui.notify('Upload finished', type = 'positive', position = 'top')

    @staticmethod
    def _source_text_mis_notify() -> None:
        ui.notify(f'Upload text file or enter some text below', type = 'negative', position = 'top')

    @staticmethod
    def _upload_error_notify() -> None:
        ui.notify(f'Invalid input file. Use a different one or paste some text below', type = 'negative', position = 'top')

    def _upload_rejected_notify(self) -> None:
        ui.notify(f'Upload a text file with max: {self.max_file_size / 10 ** 3} KB', type = 'negative', position = 'top')

    @staticmethod
    def _upload_success_notify() -> None:
        ui.notify('Upload finished', type = 'positive', position = 'top')

    def _header(self) -> None:
        with ui.header().classes('justify-between'):
            ui.button(text = 'START PAGE', on_click = self._open_start_page)
            ui.label('UPLOAD').classes('absolute-center')
            ui.space()
            ui.button(text = 'DICTIONARIES', on_click = self._open_dictionaries)
            ui.button(icon = 'settings', on_click = self._open_settings)

    def _center(self) -> None:
        with ui.card().classes(f'{self.abs_top_center(50)} w-[80%] h-[90%]') \
                .style('align-items: center; min-width: 1000px'):
            ui.button(icon = 'help', on_click = None).classes('absolute-top-right')
            ui.label('Upload a text file or enter some text below').style('font-size: 14pt')
            self.ui_uploader = ui.upload(
                # label = 'select path',
                on_upload = self._upload_handler,
                on_rejected = self._upload_rejected_notify,
                max_file_size = self.max_file_size,
                auto_upload = self.auto_upload,
                max_files = self.max_files) \
                .props('accept=.txt flat dense')
            self.ui_text_box = ui.textarea(
                label = 'Enter some text',
                placeholder = 'start typing',
                on_change = None) \
                .classes('w-full h-full flex-grow') \
                .style('min-width: 1000px; min-height: 500px; font-size: 12pt')
            self._language_selector()

    def _language_selector(self):
        languages = self.decoder.get_supported_languages()
        with ui.row():
            self.ui_scr_select = ui.select(
                label = 'Source language',
                value = 'auto',
                options = ['auto'] + languages,
                on_change = self._update_text) \
                .props('dense options-dense') \
                .style('min-width: 200px; font-size: 12pt')
            ui.space()
            self.ui_tar_select = ui.select(
                label = 'Target language',
                value = 'english',
                options = languages,
                on_change = self._update_text) \
                .props('dense options-dense') \
                .style('min-width: 200px; font-size: 12pt')
            ui.space()
            ui.button(icon = 'save', on_click = self._update_text)
            ui.space()
            ui.button(text = 'Decode', on_click = self._open_decoding)
            ui.button(icon = 'delete', on_click = self._clear_text).classes('absolute-bottom-right')
            self._load_text()

    def page(self) -> None:
        self.__init_ui__()
        self._header()
        self._center()
