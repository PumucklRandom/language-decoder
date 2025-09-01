import time
import asyncio
from urllib import parse
from typing import Any, Callable
from abc import ABC, abstractmethod
from fastapi.responses import Response
from nicegui.storage import PURGE_INTERVAL
from nicegui import ui, app, Client, background_tasks
from backend.logger.logger import logger
from backend.config.config import CONFIG
from backend.user_data.settings import Settings
from backend.user_data.dictionaries import Dicts
from backend.decoder.language_decoder import LanguageDecoder
from frontend.pages.ui.config import URLS, COLORS, UILabels, get_ui_labels
from frontend.pages.ui.error import catch
from frontend.pages.ui.state import State

pages_lock = asyncio.Lock()


class Classproperty(property):
    def __init__(self, fget = None, fset = None, fdel = None, doc = None):
        super().__init__(fget, fset, fdel, doc)

    def __get__(self, instance, owner = None):
        return super().__get__(owner)

    def __set__(self, instance, value):
        super().__set__(type(instance), value)

    def __delete__(self, instance):
        super().__delete__(type(instance))


class Page(ABC):
    """
    Basic class for all pages with integrated URL path, state, backend, page navigation and app routing
    """

    __slots__ = (
        'state',
        'word_limit',
        'max_file_size',
        'max_decode_size',
        'auto_upload',
        'max_files',
    )
    _URL: str

    @Classproperty
    def URL(self) -> str:
        return self._URL

    def __init__(self) -> None:
        self.state: State = None  # type: ignore
        self.word_limit: int = CONFIG.word_limit
        self.max_file_size: int = self.word_limit * 50
        self.max_decode_size: int = self.max_file_size * 2
        self.auto_upload: bool = CONFIG.Upload.auto_upload
        self.max_files: int = CONFIG.Upload.max_files

    @property
    def time_stamp(self) -> float:
        return self.state.time_stamp

    @property
    def decoder(self) -> LanguageDecoder:
        return self.state.decoder

    @property
    def dicts(self) -> Dicts:
        return self.decoder.dicts

    @property
    def settings(self) -> Settings:
        return self.decoder.settings

    @property
    def UI_LABELS(self) -> UILabels:
        return self.state.ui_labels

    @property
    def show_tips(self) -> bool:
        return self.settings.app.show_tips

    def __init_ui__(self) -> None:
        if self.state is None: self.state = State(storage = app.storage.tab)
        if self.state.user_uuid == '': self.state.user_uuid = app.storage.browser.get('id')
        if self.decoder is None: self.state.decoder = LanguageDecoder(user_uuid = self.state.user_uuid)
        self.settings.load()
        if self.state.ui_labels is None: self.get_ui_labels()
        ui.dark_mode().set_value(self.settings.app.dark_mode)
        # TODO: maybe there is a way to set the default colors instead of overwriting the colors after each reload
        ui.colors(primary = COLORS.PRIMARY.VAL, secondary = COLORS.SECONDARY.VAL, accent = COLORS.ACCENT.VAL,
                  dark = COLORS.DARK.VAL, dark_page = COLORS.DARK_PAGE.VAL, positive = COLORS.POSITIVE.VAL,
                  negative = COLORS.NEGATIVE.VAL, info = COLORS.INFO.VAL, warning = COLORS.WARNING.VAL)

    @catch
    def get_ui_labels(self) -> None:
        self.state.ui_labels = get_ui_labels(self.settings.app.language)

    @staticmethod
    @catch
    def goto(url: str, call: Callable = None) -> None:
        if call:
            call()
        if url == 'back':
            ui.navigate.back()
        else:
            ui.navigate.to(url)

    @staticmethod
    def _add_app_route(route: str, content: Any, file_type: str, disposition: str, filename: str) -> None:
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

    def _upd_app_route(self, url: str, content: Any, file_type: str,
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

    async def open_route(self, content: Any, file_type: str,
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

    @catch
    def _task_cancel(self) -> None:
        if self.state.task is None: return
        self.state.task.cancel()

    @abstractmethod
    async def page(self) -> None:
        pass


class UIPage(ui.page):
    """
    A wrapper for the nicegui page class which:
    - passes the URL path for each page
    - generate a new page instance for every user
    - builds the pages
    """

    __slots__ = ('page_class',)

    pages: dict[str, Page] = {}

    @classmethod
    async def prune_pages(cls):
        while True:
            async with pages_lock:
                for page_id, page in list(cls.pages.items()):
                    if time.time() > page.time_stamp + CONFIG.session_time:
                        del cls.pages[page_id]
            try:
                await asyncio.sleep(PURGE_INTERVAL)
            except asyncio.CancelledError:
                logger.info('Cancelled prune_pages')
                break

    @classmethod
    def create_prune_task(cls):
        logger.info('Create prune_pages task')
        background_tasks.create(cls.prune_pages(), name = 'prune_pages')

    def __init__(self, page_class: type[Page]) -> None:
        super().__init__(path = page_class.URL)
        self.page_class = page_class

    async def page(self, client: Client) -> None:
        await client.connected()
        page_id = f'{self.page_class.__name__}_{client.tab_id}'
        async with pages_lock:
            if page_id not in self.pages:
                # for every page_class and user_tab a new page instance is created
                self.pages[page_id] = self.page_class()
            # call the page instance to render the page
            await self.pages[page_id].page()

    def build(self) -> None:
        self(self.page)
