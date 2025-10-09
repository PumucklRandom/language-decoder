import os
import sys
from nicegui import ui, app
from backend.config.config import CONFIG
from frontend.pages.ui.page_abc import UIPage
from frontend.pages.start import Start
from frontend.pages.upload import Upload
from frontend.pages.decoding import Decoding
from frontend.pages.dictionaries import Dictionaries
from frontend.pages.settings import Settings

dir_path = os.path.dirname(os.path.relpath(__file__))
native = CONFIG.native if sys.platform != 'linux' else False
window_size = CONFIG.window_size if native else None


def build() -> None:
    # Every page is build here
    UIPage(Start).build()
    UIPage(Upload).build()
    UIPage(Decoding).build()
    UIPage(Dictionaries).build()
    UIPage(Settings).build()
    app.on_startup(UIPage.create_prune_task)


def run() -> None:
    ui.run(
        host = CONFIG.host,
        port = CONFIG.port,
        title = CONFIG.title,
        favicon = os.path.join(dir_path, CONFIG.favicon),
        dark = CONFIG.dark,
        binding_refresh_interval = CONFIG.debounce / 1000,
        reconnect_timeout = CONFIG.reconnect_timeout,
        native = native,
        window_size = window_size,
        fullscreen = CONFIG.fullscreen,
        frameless = CONFIG.frameless,
        reload = CONFIG.reload,
        storage_secret = CONFIG.storage_secret
    )
