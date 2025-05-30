from nicegui import ui, Client
from frontend.pages.ui.config import URLS
from frontend.pages.ui.error import catch
from frontend.pages.ui.page_abc import Page


class Start(Page):
    _URL = URLS.START

    def __init__(self) -> None:
        super().__init__()
        self.font_size = 14

    @catch
    def _center(self) -> None:
        with ui.column().style(f'font-size:{self.font_size}pt').classes('w-full items-center'):
            self._explanation()
            ui.separator()
            self._disclaimer()

    @catch
    def _explanation(self) -> None:
        with ui.card().style('min-width:1000px; min-height:562px; height:60vh').classes('w-[60%] items-center'):
            ui.label(text = self.UI_LABELS.START.Explanations.title) \
                .style(f'font-size:{self.font_size * 1.2}pt')
            labels = ' '.join(self.UI_LABELS.START.Explanations.text[:-2])
            ui.label(text = labels)
            with ui.row().style('gap:0.0rem'):
                ui.label(text = self.UI_LABELS.START.Explanations.text[-2])
                ui.space().style(f'width:{self.font_size / 2}px')
                ui.link(
                    text = self.UI_LABELS.START.Explanations.text[-1],
                    target = self.UI_LABELS.START.Explanations.link,
                    new_tab = True
                )
            ui.space()
            ui.button(text = self.UI_LABELS.START.Explanations.start,
                      on_click = lambda: self.goto(URLS.UPLOAD)).style(f'font-size:{self.font_size}pt')
            ui.space()

    @catch
    def _disclaimer(self) -> None:
        with ui.column().style(f'min-width:1000px; font-size:{self.font_size * 0.8}pt') \
                .classes('w-[60%] items-center'):
            ui.label(text = self.UI_LABELS.START.Disclaimers.title) \
                .style(f'font-size:{self.font_size}pt')
            labels = ''
            for label in self.UI_LABELS.START.Disclaimers.text[:-2]:
                labels += f'{label} '
            ui.label(text = labels)
            with ui.row().style('gap:0.0rem'):
                ui.label(text = self.UI_LABELS.START.Disclaimers.text[-2])
                ui.space().style(f'width:{self.font_size * 0.8 / 2}px')
                ui.link(
                    text = self.UI_LABELS.START.Disclaimers.text[-1],
                    target = self.UI_LABELS.START.Disclaimers.link,
                    new_tab = True
                )

    async def page(self, client: Client) -> None:
        await self.__init_ui__(client = client)
        self._center()
