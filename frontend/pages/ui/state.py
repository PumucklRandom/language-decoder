from typing import Any, List, Union
from copy import copy
from backend.config.config import CONFIG
from frontend.pages.ui.config import Language


class State(object):

    def __init__(self, store: dict):
        self.store = store

    def get(self, key, dflt: any = None):
        return self.store.get(key, dflt)

    def update(self, key: str, value: Any) -> None:
        self.store.update({key: value})

    def add(self, key: str, value: Any) -> None:
        if key not in self.store: self.update(key, value)

    def keys(self):
        return self.store.keys()

    def values(self):
        return self.store.values()

    def items(self):
        return self.store.items()

    def clear(self):
        self.store.clear()

    def pop(self, key: str):
        self.store.pop(key)

    def copy(self, store: bool = False) -> Union[dict, object]:
        if store:
            return self.store.copy()
        return copy(self)

    @property
    def id(self) -> str:
        return self.get('id')

    @id.setter
    def id(self, value: str) -> None:
        self.update('id', value)

    @property
    def uuid(self) -> str:
        return self.get('uuid')

    @uuid.setter
    def uuid(self, value: str) -> None:
        self.update('uuid', value)

    @property
    def url_history(self) -> type(object):
        return self.get('url_history')

    @url_history.setter
    def url_history(self, value: type(object)) -> None:
        self.update('url_history', value)

    @property
    def ui_language(self) -> Language:
        return self.get('ui_language')

    @ui_language.setter
    def ui_language(self, value: Language) -> None:
        self.update('ui_language', value)

    @property
    def language(self) -> str:
        return self.get('language', 'english')

    @language.setter
    def language(self, value: str) -> None:
        self.update('language', value)

    @property
    def dark_mode(self) -> bool:
        return self.get('dark_mode', CONFIG.dark)

    @dark_mode.setter
    def dark_mode(self, value: bool) -> None:
        self.update('dark_mode', value)

    @property
    def show_tips(self) -> bool:
        return self.get('show_tips', True)

    @show_tips.setter
    def show_tips(self, value: bool) -> None:
        self.update('show_tips', value)

    @property
    def reformatting(self) -> bool:
        return self.get('reformatting', True)

    @reformatting.setter
    def reformatting(self, value: bool) -> None:
        self.update('reformatting', value)

    @property
    def http(self) -> str:
        return self.get('http')

    @http.setter
    def http(self, value: str) -> None:
        self.update('http', value)

    @property
    def https(self) -> str:
        return self.get('https')

    @https.setter
    def https(self, value: str) -> None:
        self.update('https', value)

    @property
    def proxies(self) -> dict:
        return self.get('proxies', {})

    @proxies.setter
    def proxies(self, value: dict) -> None:
        self.update('proxies', value)

    @property
    def pdf_params(self) -> dict:
        return self.get('pdf_params', CONFIG.Pdf.__dict__.copy())

    @pdf_params.setter
    def pdf_params(self, value: dict) -> None:
        self.update('pdf_params', value)

    @property
    def regex(self) -> CONFIG.Regex:
        return self.get('regex', CONFIG.Regex.copy())

    @regex.setter
    def regex(self, value: CONFIG.Regex) -> None:
        self.update('regex', value)

    @property
    def dict_name(self) -> str:
        return self.get('dict_name')

    @dict_name.setter
    def dict_name(self, value: str) -> None:
        self.update('dict_name', value)

    @property
    def title(self) -> str:
        return self.get('title')

    @title.setter
    def title(self, value: str) -> None:
        self.update('title', value)

    @property
    def source_language(self) -> str:
        return self.get('source_language', 'auto')

    @source_language.setter
    def source_language(self, value: str) -> None:
        self.update('source_language', value)

    @property
    def target_language(self) -> str:
        return self.get('target_language', 'english')

    @target_language.setter
    def target_language(self, value: str) -> None:
        self.update('target_language', value)

    @property
    def source_text(self) -> str:
        return self.get('source_text', '')

    @source_text.setter
    def source_text(self, value: str) -> None:
        self.update('source_text', value)

    @property
    def source_words(self) -> List[str]:
        return self.get('source_words', [])

    @source_words.setter
    def source_words(self, value: List[str]) -> None:
        self.update('source_words', value)

    @property
    def target_words(self) -> List[str]:
        return self.get('target_words', [])

    @target_words.setter
    def target_words(self, value: List[str]) -> None:
        self.update('target_words', value)

    @property
    def sentences(self) -> List[str]:
        return self.get('sentences', [])

    @sentences.setter
    def sentences(self, value: List[str]) -> None:
        self.update('sentences', value)

    @property
    def content(self) -> bytes:
        return self.get('content', b'')

    @content.setter
    def content(self, value: bytes) -> None:
        self.update('content', value)

    @property
    def s_hash(self) -> int:
        return self.get('s_hash', 0)

    @s_hash.setter
    def s_hash(self, value: int) -> None:
        self.update('s_hash', value)

    @property
    def d_hash(self) -> int:
        return self.get('d_hash', 0)

    @d_hash.setter
    def d_hash(self, value: int) -> None:
        self.update('d_hash', value)

    @property
    def c_hash(self) -> int:
        return self.get('c_hash', 0)

    @c_hash.setter
    def c_hash(self, value: int) -> None:
        self.update('c_hash', value)
