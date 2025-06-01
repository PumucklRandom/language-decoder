from backend.config.config import CONFIG
from backend.decoder.language_decoder import LanguageDecoder
from frontend.pages.ui.config import UILabels


class State(object):
    __slots__ = ('_storage',)

    def __init__(self, storage: dict) -> None:
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
    def ui_labels(self) -> UILabels:
        return self.get('ui_labels', None)

    @ui_labels.setter
    def ui_labels(self, value: UILabels) -> None:
        self._storage['ui_labels'] = value

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
    def c_hash(self) -> int:
        return self.get('c_hash', 0)

    @c_hash.setter
    def c_hash(self, value: int) -> None:
        self._storage['c_hash'] = value

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
