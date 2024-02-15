from typing import List
from abc import ABC, abstractmethod
from nicegui import ui, app
from backend.config.const import CONFIG
from backend.utils import utilities as utils
from backend.decoder.language_decoder import LanguageDecoder
from frontend.pages.ui_custom import COLORS, HTML, Language, ui_language

# It is very important to initialize the LanguageDecoder instance outside the initialization of the Page class,
# so that all inherited Page classes have the same LanguageDecoder state!
language_decoder = LanguageDecoder()


class Settings(object):
    show_tips: bool = True
    dark_mode: bool = True
    language: str = 'english'


settings = Settings()


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


url_history = URLHistory()


class Page(ABC, ui.page):
    """
    Basic class for all pages with integrated URL history and a self build functionality
    """

    def __init__(self, url) -> None:
        super().__init__(path = url)
        self._URL: str = url
        self._url_history: URLHistory = url_history
        self._app: app = app
        self.ui_language: Language = ui_language
        self.utils: utils = utils
        self.decoder: LanguageDecoder = language_decoder
        self.pdf: dict = CONFIG.pdf.__dict__.copy()
        self.settings: Settings = settings

    def __init_ui__(self):
        self.decoder.uuid = self._app.storage.browser.get('id')
        ui.dark_mode().bind_value_from(self.settings, 'dark_mode')
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

    @property
    def show_tips(self):
        return self.settings.show_tips

    @property
    def _language(self):
        return self.settings.language

    def build(self) -> None:
        self(self.page)

    @abstractmethod
    def page(self, *args, **kwargs) -> None:
        pass
