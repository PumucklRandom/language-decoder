from nicegui import ui
from backend.logger.logger import logger
from frontend.pages.ui.config import URLS
from frontend.pages.ui.page_abc import Page


class Start(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.START)
        self.font_size = 14

    def _open_upload(self) -> None:
        try:
            self.update_url_history()
            ui.open(f'{URLS.UPLOAD}')
        except Exception as exception:
            logger.error(f'Error in "_open_upload" with exception:\n{exception}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _center(self) -> None:
        try:
            with ui.column().classes('w-full items-center').style(f'font-size:{self.font_size}pt'):
                self._explanation()
                ui.separator()
                self._disclaimer()
        except Exception as exception:
            logger.error(f'Error in "_center with" exception:\n{exception}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _explanation(self) -> None:
        try:
            with ui.card().classes('w-[60%] items-center') \
                    .style('min-width:1000px; min-height:562px; height:60vh'):
                ui.label(text = self.ui_language.START.Explanations.title) \
                    .style(f'font-size:{self.font_size * 1.2}pt')
                labels = ''
                for label in self.ui_language.START.Explanations.text[:-2]:
                    labels += f'{label} '
                ui.label(text = labels)
                with ui.row().style('gap:0.0rem'):
                    ui.label(text = self.ui_language.START.Explanations.text[-2])
                    ui.space().style(f'width:{self.font_size / 2}px')
                    ui.link(
                        text = self.ui_language.START.Explanations.text[-1],
                        target = self.ui_language.START.Explanations.link,
                        new_tab = True
                    )
                ui.space()
                ui.button(text = self.ui_language.START.Explanations.start, on_click = self._open_upload) \
                    .style(f'font-size:{self.font_size}pt')
                ui.space()
        except Exception as exception:
            logger.error(f'Error in "_explanation" with exception:\n{exception}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def _disclaimer(self) -> None:
        try:
            with ui.column().classes('w-[60%] items-center') \
                    .style(f'min-width:1000px; font-size:{self.font_size * 0.8}pt'):
                ui.label(text = self.ui_language.START.Disclaimers.title) \
                    .style(f'font-size:{self.font_size}pt')
                labels = ''
                for label in self.ui_language.START.Disclaimers.text[:-2]:
                    labels += f'{label} '
                ui.label(text = labels)
                with ui.row().style('gap:0.0rem'):
                    ui.label(text = self.ui_language.START.Disclaimers.text[-2])
                    ui.space().style(f'width:{self.font_size * 0.8 / 2}px')
                    ui.link(
                        text = self.ui_language.START.Disclaimers.text[-1],
                        target = self.ui_language.START.Disclaimers.link,
                        new_tab = True
                    )
        except Exception as exception:
            logger.error(f'Error in "_disclaimer" with exception:\n{exception}')
            ui.notify(self.ui_language.GENERAL.Error.internal, type = 'negative', position = 'top')

    def page(self) -> None:
        self.__init_ui__()
        self._center()
