import asyncio
from urllib import parse
from abc import ABC, abstractmethod
from nicegui import ui, app, Client
from fastapi.responses import Response
from backend.config.config import CONFIG
from backend.decoder.language_decoder import LanguageDecoder
from backend.dictionaries.dictionaries import Dicts
from frontend.pages.ui.config import URLS, COLORS, UILabels
from frontend.pages.ui.error import catch
from frontend.pages.ui.state import State


class Classproperty(property):
    def __get__(self, obj, objtype = None):
        return super(Classproperty, self).__get__(objtype)

    def __set__(self, obj, value):
        super(Classproperty, self).__set__(type(obj), value)

    def __delete__(self, obj):
        super(Classproperty, self).__delete__(type(obj))


class Page(ABC):
    """
    Basic class for all pages with integrated URL history and a self build functionality
    """
    _URL: str

    def __init__(self) -> None:
        self.state: State
        self.word_limit: int = CONFIG.word_limit
        self.max_file_size: int = self.word_limit * 50
        self.max_decode_size: int = self.max_file_size * 2
        self.auto_upload: bool = CONFIG.Upload.auto_upload
        self.max_files: int = CONFIG.Upload.max_files

    @property
    def decoder(self) -> LanguageDecoder:
        return self.state.decoder

    @property
    def dicts(self) -> Dicts:
        return self.decoder.dicts

    @property
    def UI_LABELS(self) -> UILabels:
        return self.state.ui_labels

    async def __init_ui__(self, client: Client) -> None:
        await client.connected()
        self.state = State(storage = app.storage.tab)
        if self.state.uuid == '': self.state.uuid = app.storage.tab.get('uuid')
        if self.state.user_uuid == '': self.state.user_uuid = app.storage.browser.get('id')
        if self.decoder is None: self.state.decoder = LanguageDecoder(user_uuid = self.state.user_uuid)
        ui.dark_mode().set_value(self.state.dark_mode)
        # TODO: maybe there is a way to set the default colors instead of overwriting the colors after each reload
        ui.colors(primary = COLORS.PRIMARY.VAL, secondary = COLORS.SECONDARY.VAL, accent = COLORS.ACCENT.VAL,
                  dark = COLORS.DARK.VAL, dark_page = COLORS.DARK_PAGE.VAL, positive = COLORS.POSITIVE.VAL,
                  negative = COLORS.NEGATIVE.VAL, info = COLORS.INFO.VAL, warning = COLORS.WARNING.VAL)

    @Classproperty
    def URL(cls) -> str:
        return cls._URL

    @staticmethod
    @catch
    def goto(url: str, call: callable = None) -> None:
        if call:
            call()
        if url == 'back':
            ui.navigate.back()
        else:
            ui.navigate.to(url)

    @staticmethod
    def _add_app_route(route: str, content: any, file_type: str, disposition: str, filename: str) -> None:
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
    def _del_app_routes(route: str) -> None:
        app.routes[:] = [app_route for app_route in app.routes if not app_route.path.startswith(route)]

    def _upd_app_route(self, url: str, content: any, file_type: str,
                       filename: str, disposition: str = 'attachment') -> str:
        route = f'{url}{self.state.uuid}/{self.state.user_uuid}'
        if disposition == 'attachment':
            route = f'{route}.{file_type}'
        else:
            route = f'{route}/'
        self._del_app_routes(route = route)
        self._add_app_route(
            route = route,
            content = content,
            file_type = file_type,
            disposition = disposition,
            filename = filename
        )
        return route

    async def open_route(self, content: any, file_type: str,
                         filename: str, disposition: str = 'attachment') -> None:
        route = self._upd_app_route(
            url = URLS.DOWNLOAD,
            content = content,
            file_type = file_type,
            filename = filename,
            disposition = disposition
        )
        if disposition == 'attachment':
            ui.download(route)
        else:
            ui.navigate.to(f'{route}', new_tab = True)
        try:
            await asyncio.wait_for(ui.context.client.disconnected(), timeout = CONFIG.route_timeout)
        except asyncio.TimeoutError:
            self._del_app_routes(route = route)

    @abstractmethod
    async def page(self, client: Client) -> None:
        pass


class UIPage(ui.page):
    def __init__(self, page_class: type(Page)) -> None:
        super().__init__(path = page_class.URL)
        self.page_class = page_class

    async def page(self, client: Client) -> None:
        # for every user a new page instance is generated
        page_instance = self.page_class()
        await page_instance.page(client = client)

    def build(self) -> None:
        self(self.page)
