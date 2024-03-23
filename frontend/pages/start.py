from nicegui import ui
from backend.config.config import URLS
from frontend.pages.page_abc import Page


class Start(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.START)
        self.font_size = 14

    def _open_upload(self) -> None:
        self.update_url_history()
        ui.open(f'{URLS.UPLOAD}')

    def _center(self) -> None:
        with ui.column().classes('w-full items-center').style(f'font-size:{self.font_size}pt'):
            self._explanation()
            ui.separator()
            self._disclaimer()

    def _explanation(self) -> None:
        with ui.card().classes('w-[60%] items-center').style('min-width:1000px; min-height:562px; height:60vh'):
            ui.label(text = self.ui_language.START.Explanations[0]).style(f'font-size:{self.font_size * 1.2}pt')
            labels = ''
            for label in self.ui_language.START.Explanations[1]:
                labels += f'{label} '
            ui.label(text = labels)
            with ui.row().style('gap:0.0rem'):
                ui.label(text = self.ui_language.START.Explanations[2][0])
                ui.space().style(f'width:{self.font_size / 2}px')
                ui.link(
                    text = self.ui_language.START.Explanations[2][1],
                    target = '''
                    https://blog.brain-friendly.com/easy-language-learning-by-vera-f-birkenbihl-the-decoding-method/
                    ''',
                    new_tab = True)
            ui.space()
            ui.button(text = 'START', on_click = self._open_upload).style(f'font-size:{self.font_size}pt')
            ui.space()

    def _disclaimer(self) -> None:
        with (ui.column().classes('w-[60%] items-center') \
                      .style(f'min-width:1000px; font-size:{self.font_size * 0.8}pt')):
            ui.label(text = self.ui_language.START.Disclaimers[0]).style(f'font-size:{self.font_size}pt')
            for label in self.ui_language.START.Disclaimers[1:-1]:
                ui.label(text = ' '.join(label))
            with ui.row().style('gap:0.0rem'):
                ui.label(text = self.ui_language.START.Disclaimers[-1])
                ui.space().style(f'width:{self.font_size * 0.8 / 2}px')
                ui.link(
                    text = 'Github.com.',
                    target = 'https://github.com/PumucklRandom/language-decoder/',
                    new_tab = True)

    def page(self) -> None:
        self.__init_ui__()
        self._center()
