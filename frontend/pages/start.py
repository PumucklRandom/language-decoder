from nicegui import ui
from frontend.pages.ui.error import catch
from frontend.pages.ui.config import URLS
from frontend.pages.ui.page_abc import Page


class Start(Page):
    __slots__ = ()

    _URL = URLS.START

    def __init__(self) -> None:
        super().__init__()

    @catch
    def _center(self) -> None:
        with ui.column().classes('w-full items-center'). \
                style('font-size:14pt'):
            self._explanation()
            ui.separator()
            self._disclaimer()

    @catch
    def _explanation(self) -> None:
        with ui.card().classes('w-[60%] items-center'). \
                style('min-width:1000px; min-height:562px; height:60vh'):
            ui.label(text = self.UI_LABELS.START.Explanations.title) \
                .style('font-size:18pt')
            ui.label(text = ' '.join(self.UI_LABELS.START.Explanations.text[:-2]))
            with ui.row().style('gap:0.0rem'):
                ui.label(text = self.UI_LABELS.START.Explanations.text[-2])
                ui.space().style('width:6px')
                ui.link(
                    text = self.UI_LABELS.START.Explanations.text[-1],
                    target = self.UI_LABELS.START.Explanations.link,
                    new_tab = True
                )
            ui.space()
            ui.button(text = self.UI_LABELS.START.Explanations.start,
                      on_click = lambda: self.goto(URLS.UPLOAD)).style('font-size:14pt')
            ui.space()

    @catch
    def _disclaimer(self) -> None:
        with ui.column().classes('w-[60%] items-center') \
                .style('min-width:1000px; font-size:11pt'):
            ui.label(text = self.UI_LABELS.START.Disclaimers.title) \
                .style('font-size:14pt')
            labels = ''
            for label in self.UI_LABELS.START.Disclaimers.text[:-2]:
                labels += '{label} '
            ui.label(text = labels)
            with ui.row().style('gap:0.0rem'):
                ui.label(text = self.UI_LABELS.START.Disclaimers.text[-2])
                ui.space().style('width:4px')
                ui.link(
                    text = self.UI_LABELS.START.Disclaimers.text[-1],
                    target = self.UI_LABELS.START.Disclaimers.link,
                    new_tab = True
                )

    async def page(self) -> None:
        self.__init_ui__()
        self._center()
