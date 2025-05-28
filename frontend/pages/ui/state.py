from typing import Dict
from backend.config.config import CONFIG
from backend.decoder.language_decoder import LanguageDecoder
from backend.dictionaries.dictionaries import Dicts
from frontend.pages.ui.config import UILabels, UI_LABELS


class State(object):
    __slots__ = ('_storage',)

    def __init__(self, storage: Dict[str, any]) -> None:
        super().__setattr__('_storage', storage)

    def __setattr__(self, name: str, value: any):
        if name == '_storage':
            super().__setattr__(name, value)
        self._storage[name] = value

    def __getattr__(self, name: str) -> any:
        return self.get(name, None)

    def add(self, name: str, value: any) -> None:
        self._storage.setdefault(name, value)

    def get(self, name: str, default: any = None) -> any:
        return self._storage.setdefault(name, default)

    def keys(self):
        return self._storage.keys()

    def values(self):
        return self._storage.values()

    def items(self):
        return self._storage.items()

    def pop(self, name: str):
        self._storage.pop(name, None)

    def clear(self):
        self._storage.clear()

    @property
    def uuid(self) -> str:
        return self.get('uuid', '')

    @uuid.setter
    def uuid(self, value: str) -> None:
        self._storage['uuid'] = value

    @property
    def user_uuid(self) -> str:
        return self.get('user_uuid', '')

    @user_uuid.setter
    def user_uuid(self, value: str) -> None:
        self._storage['user_uuid'] = value

    @property
    def decoder(self) -> LanguageDecoder:
        return self.get('decoder', None)

    @decoder.setter
    def decoder(self, value: LanguageDecoder) -> None:
        self._storage['decoder'] = value

    @property
    def dicts(self) -> Dicts:
        return self.get('dicts', None)

    @dicts.setter
    def dicts(self, value: Dicts) -> None:
        self._storage['dicts'] = value

    @property
    def ui_labels(self) -> UILabels:
        return self.get('ui_labels', UI_LABELS)

    @ui_labels.setter
    def ui_labels(self, value: UILabels) -> None:
        self._storage['ui_labels'] = value

    @property
    def language(self) -> str:
        return self.get('language', 'english')

    @language.setter
    def language(self, value: str) -> None:
        self._storage['language'] = value

    @property
    def dark_mode(self) -> bool:
        return self.get('dark_mode', CONFIG.dark)

    @dark_mode.setter
    def dark_mode(self, value: bool) -> None:
        self._storage['dark_mode'] = value

    @property
    def show_tips(self) -> bool:
        return self.get('show_tips', True)

    @show_tips.setter
    def show_tips(self, value: bool) -> None:
        self._storage['show_tips'] = value

    @property
    def source_words(self) -> list[str]:
        return self.get('source_words', [])

    @source_words.setter
    def source_words(self, value: list[str]) -> None:
        self._storage['source_words'] = value

    @property
    def target_words(self) -> list[str]:
        return self.get('target_words', [])

    @target_words.setter
    def target_words(self, value: list[str]) -> None:
        self._storage['target_words'] = value

    @property
    def sentences(self) -> list[str]:
        return self.get('sentences', [])

    @sentences.setter
    def sentences(self, value: list[str]) -> None:
        self._storage['sentences'] = value

    @property
    def source_text(self) -> str:
        return self.get('source_text', '')

    @source_text.setter
    def source_text(self, value: str) -> None:
        self._storage['source_text'] = value

    @property
    def source_language(self) -> str:
        return self.get('source_language', 'auto')

    @source_language.setter
    def source_language(self, value: str) -> None:
        self._storage['source_language'] = value

    @property
    def target_language(self) -> str:
        return self.get('target_language', 'english')

    @target_language.setter
    def target_language(self, value: str) -> None:
        self._storage['target_language'] = value

    @property
    def title(self) -> str:
        return self.get('title', '')

    @title.setter
    def title(self, value: str) -> None:
        self._storage['title'] = value

    @property
    def content(self) -> bytes:
        return self.get('content', b'')

    @content.setter
    def content(self, value: bytes) -> None:
        self._storage['content'] = value

    @property
    def pdf_params(self) -> dict:
        return self.get('pdf_params', CONFIG.Pdf.__dict__.copy())

    @pdf_params.setter
    def pdf_params(self, value: dict) -> None:
        self._storage['pdf_params'] = value

    @property
    def c_hash(self) -> int:
        return self.get('c_hash', 0)

    @c_hash.setter
    def c_hash(self, value: int) -> None:
        self._storage['c_hash'] = value

    @property
    def dict_name(self) -> str:
        return self.get('dict_name', None)

    @dict_name.setter
    def dict_name(self, value: str) -> None:
        self._storage['dict_name'] = value

    @property
    def table_page(self) -> dict:
        return self.get('table_page', {'page': 1, 'rowsPerPage': CONFIG.table_options[2]})

    @table_page.setter
    def table_page(self, value: dict) -> None:
        self._storage['table_page'] = value

    @property
    def grid_page(self) -> dict:
        return self.get('grid_page', {'page': 1, 'rowsPerPage': CONFIG.grid_options[2]})

    @grid_page.setter
    def grid_page(self, value: dict) -> None:
        self._storage['grid_page'] = value

    @property
    def decode(self) -> bool:
        return self.get('decode', False)

    @decode.setter
    def decode(self, value: bool) -> None:
        self._storage['decode'] = value

    @property
    def find(self) -> str:
        return self.get('find', '')

    @find.setter
    def find(self, value: str) -> None:
        self._storage['find'] = value

    @property
    def repl(self) -> str:
        return self.get('repl', '')

    @repl.setter
    def repl(self, value: str) -> None:
        self._storage['repl'] = value

    @property
    def proxies(self) -> dict:
        return self.get('proxies', {})

    @proxies.setter
    def proxies(self, value: dict) -> None:
        self._storage['proxies'] = value

    @property
    def http(self) -> str:
        return self.get('http', '')

    @http.setter
    def http(self, value: str) -> None:
        self._storage['http'] = value

    @property
    def https(self) -> str:
        return self.get('https', '')

    @https.setter
    def https(self, value: str) -> None:
        self._storage['https'] = value

    @property
    def regex(self) -> CONFIG.Regex:
        return self.get('regex', CONFIG.Regex.copy())

    @regex.setter
    def regex(self, value: CONFIG.Regex) -> None:
        self._storage['regex'] = value

    @property
    def reformatting(self) -> bool:
        return self.get('reformatting', True)

    @reformatting.setter
    def reformatting(self, value: bool) -> None:
        self._storage['reformatting'] = value

    @property
    def alt_trans(self) -> bool:
        return self.get('alt_trans', False)

    @alt_trans.setter
    def alt_trans(self, value: bool) -> None:
        self._storage['alt_trans'] = value
