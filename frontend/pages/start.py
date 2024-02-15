from nicegui import ui
from backend.config.const import URLS
from frontend.pages.page_abc import Page


class Start(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.START)

    def _open_upload(self) -> None:
        self.update_url_history()
        ui.open(f'{URLS.UPLOAD}')

    def _center(self) -> None:
        with ui.column().classes('w-full items-center').style('font-size:12pt'):
            with ui.card().classes('w-[60%] items-center').style('min-width:1000px; min-height:562px; height:60vh'):
                for label in self.ui_language.START.Explanations:
                    ui.label(text = label)
                ui.button(text = 'START', on_click = self._open_upload)
            ui.separator()
            for label in self.ui_language.START.Disclaimers:
                ui.label(text = label)

    def page(self) -> None:
        self.__init_ui__()
        self._center()
