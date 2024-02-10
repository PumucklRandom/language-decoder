from typing import List
from abc import ABC, abstractmethod
from nicegui import ui, app
from backend.utils import utilities as utils
from backend.decoder.language_decoder import LanguageDecoder
from frontend.pages.ui_config import COLORS, HTML

# It is very important to initialize the LanguageDecoder instance outside the initialization of the Page class,
# so that all inherited Page classes have the same LanguageDecoder state!
language_decoder = LanguageDecoder()


class URLHistory(object):
    """
     Stores the URL of previous viewed pages to provide the GO BACK option
    """

    def __init__(self, size: int = 3) -> None:
        self.size = size
        self._url_history: List[str] = ['/'] * self.size

    @property
    def url_history(self) -> List[str]:
        return self._url_history

    def update(self, url) -> None:
        self._url_history.insert(0, url)


URL_HISTORY = URLHistory()


class Page(ABC, ui.page):
    """
    Basic class for all pages with integrated URL history and a self build functionality
    """

    def __init__(self, url) -> None:
        super().__init__(path = url)
        self._URL: str = url
        self._url_history: URLHistory = URL_HISTORY
        self.decoder: LanguageDecoder = language_decoder
        self.utils: utils = utils
        self.APP: app = app
        self.test = LanguageDecoder()

    def __init_ui__(self):
        self.decoder.uuid = self.APP.storage.browser.get('id')
        ui.colors(primary = COLORS.PRIMARY, secondary = COLORS.SECONDARY, accent = COLORS.ACCENT, dark = COLORS.DARK,
                  positive = COLORS.POSITIVE, negative = COLORS.NEGATIVE, info = COLORS.INFO, warning = COLORS.WARNING)
        ui.add_head_html(HTML.FLEX_GROW)
        ui.add_head_html(HTML.HEADER_STICKY)
        print(self.decoder.uuid)

    @property
    def URL(self) -> str:
        return self._URL

    @property
    def url_history(self) -> List[str]:
        return self._url_history.url_history

    @url_history.setter
    def url_history(self, url: str) -> None:
        self._url_history.update(url)

    def update_url_history(self) -> None:
        if self.url_history[0] != self.URL:
            self.url_history = self.URL

    @staticmethod
    def ui_space(width: int = 0, height: int = 0) -> None:
        """
        :param width: width space in px
        :param height: height space in px
        """
        ui.space().style(f'width: {width}px; height: {height}px')

    def build(self) -> None:
        self(self.page)

    @abstractmethod
    def page(self, *args, **kwargs) -> None:
        pass
