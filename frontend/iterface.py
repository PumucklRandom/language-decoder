import os
from nicegui import ui
from backend.config.config import CONFIG
from frontend.pages.start import Start
from frontend.pages.upload import Upload
from frontend.pages.decoding import Decoding
from frontend.pages.dictionaries import Dictionaries
from frontend.pages.settings import Settings


def build():
    # Every page is build here
    Start().build()
    Upload().build()
    Decoding().build()
    Dictionaries().build()
    Settings().build()


def run():
    ui.run(
        host = CONFIG.host,
        port = CONFIG.port,
        title = CONFIG.title,
        favicon = os.path.join(os.path.dirname(os.path.relpath(__file__)), CONFIG.favicon),
        dark = CONFIG.dark,
        reconnect_timeout = CONFIG.reconnect_timeout,
        native = CONFIG.native,
        window_size = CONFIG.window_size,
        fullscreen = CONFIG.fullscreen,
        frameless = CONFIG.frameless,
        reload = CONFIG.reload,
        storage_secret = CONFIG.storage_secret
    )
