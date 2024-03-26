from typing import List
from urllib import parse
from abc import ABC, abstractmethod
from nicegui import ui, app, Client
from fastapi.responses import Response
from backend.config.config import CONFIG
from backend.decoder.language_decoder import LanguageDecoder
from frontend.pages.ui.config import URLS, COLORS, HTML, Language, load_language

# It is very important to initialize the LanguageDecoder instance outside the initialization of the Page class,
# so that all inherited Page classes have the same LanguageDecoder state!
language_decoder = LanguageDecoder()
ui_language = load_language()


class Settings(object):
    dark_mode: bool = True
    show_tips: bool = True
    language: str = 'english'
    proxy_http: str = ''
    proxy_https: str = ''

    def get_proxies(self):
        return {'http': self.proxy_http, 'https': self.proxy_https}


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
        self.ui_language: Language = ui_language
        self.settings: Settings = settings
        self.decoder: LanguageDecoder = language_decoder
        self.pdf_params: dict = CONFIG.Pdf.__dict__.copy()
        self.max_file_size: int = CONFIG.Upload.max_file_size
        self.auto_upload: bool = CONFIG.Upload.auto_upload
        self.max_files: int = CONFIG.Upload.max_files

    def __init_ui__(self, client: Client = None) -> None:
        if client:
            client.on_disconnect(handler = lambda: self.del_app_routes(url = URLS.DOWNLOAD))
        self.decoder.uuid = app.storage.browser.get('id')
        ui.dark_mode().bind_value_from(self.settings, 'dark_mode')
        ui.colors(primary = COLORS.PRIMARY.VAL, secondary = COLORS.SECONDARY.VAL, accent = COLORS.ACCENT.VAL,
                  dark = COLORS.DARK.VAL, positive = COLORS.POSITIVE.VAL, negative = COLORS.NEGATIVE.VAL,
                  info = COLORS.INFO.VAL, warning = COLORS.WARNING.VAL)
        ui.add_head_html(HTML.FLEX_GROW)
        # ui.add_head_html(HTML.HEADER_STICKY)

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
    def show_tips(self) -> bool:
        return self.settings.show_tips

    @property
    def _language(self) -> str:
        return self.settings.language

    @staticmethod
    def _add_app_route(route: str, content: any, file_type: str, disposition: str, filename: str, ) -> None:
        @app.get(route)
        def app_route():
            return Response(
                content = content,
                media_type = f'application/{file_type}',
                headers = {
                    'Content-Disposition': f'{disposition}; filename={parse.quote(filename)}.{file_type}'
                },
            )

    @staticmethod
    def _del_app_route(route: str) -> None:
        app.routes[:] = [app_route for app_route in app.routes if app_route.path != route]

    @staticmethod
    def del_app_routes(url: str) -> None:
        for route in app.routes:
            if route.path.startswith(url):
                app.routes.remove(route)

    def upd_app_route(self, url: str, content: any, file_type: str,
                      filename: str, disposition: str = 'attachment') -> str:
        route = f'{url}{self.decoder.uuid}'
        if disposition == 'attachment':
            route = f'{route}.{file_type}'
        else:
            route = f'{route}/'
        self._del_app_route(route = route)
        self._add_app_route(
            route = route,
            content = content,
            file_type = file_type,
            disposition = disposition,
            filename = filename
        )
        return route

    def build(self) -> None:
        self(self.page)

    @abstractmethod
    def page(self, *args, **kwargs) -> None:
        pass
