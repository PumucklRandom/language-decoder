from urllib import parse
from abc import ABC, abstractmethod
from nicegui import ui, app, Client
from fastapi.responses import Response
from backend.config.config import CONFIG
from backend.decoder.language_decoder import LanguageDecoder
from frontend.pages.ui.config import URLS, COLORS, HTML, Language, load_language
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
        self.ui_language: Language
        self.decoder: LanguageDecoder = LanguageDecoder()
        self.max_file_size: int = CONFIG.Upload.max_file_size
        self.auto_upload: bool = CONFIG.Upload.auto_upload
        self.max_files: int = CONFIG.Upload.max_files

    async def __init_ui__(self, client: Client) -> None:
        await client.connected()
        self.__init_state__(uuid = client.tab_id)
        ui.dark_mode().set_value(self.state.dark_mode)
        self.ui_language = self.state.ui_language
        # TODO: maybe there is a way to set the default colors instead of overwriting the colors after each reload
        ui.colors(primary = COLORS.PRIMARY.VAL, secondary = COLORS.SECONDARY.VAL, accent = COLORS.ACCENT.VAL,
                  dark = COLORS.DARK.VAL, positive = COLORS.POSITIVE.VAL, negative = COLORS.NEGATIVE.VAL,
                  info = COLORS.INFO.VAL, warning = COLORS.WARNING.VAL)
        ui.add_head_html(HTML.FLEX_GROW)
        # ui.add_head_html(HTML.HEADER_STICKY)

    def __init_state__(self, uuid: str) -> None:
        self.state = State(store = app.storage.tab)
        self.state.add('uuid', uuid)
        self.state.add('user_uuid', app.storage.browser.get('id'))
        self.state.add('ui_language', load_language())
        self.state.add('pdf_params', CONFIG.Pdf.__dict__.copy())
        self.state.add('regex', CONFIG.Regex.copy())

    def set_decoder_state(self) -> None:
        self.decoder.user_uuid = self.state.user_uuid
        self.decoder.source_language = self.state.source_language
        self.decoder.target_language = self.state.target_language
        self.decoder.dict_name = self.state.dict_name
        self.decoder.reformatting = self.state.reformatting
        self.decoder.proxies = self.state.proxies
        self.decoder.regex = self.state.regex

    @Classproperty
    def URL(cls) -> str:
        return cls._URL

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
        for app_route in app.routes:
            if app_route.path.startswith(route):
                app.routes.remove(app_route)

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
        await ui.context.client.disconnected()
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
