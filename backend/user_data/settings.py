import os
import json
from copy import copy
from uuid import UUID
from typing import Union
from backend.error.error import SettingsError, catch
from backend.logger.logger import logger
from backend.config.config import CONFIG, Regex

file_dir = os.path.dirname(os.path.relpath(__file__))


class Settings(object):

    def __init__(self, user_uuid: Union[UUID, str] = '00000000-0000-0000-0000-000000000000',
                 setts_path: str = 'setts') -> None:
        """
        :param user_uuid: user uuid to identify the corresponding settings
        :param setts_path: path to the settings directory
        """
        self.user_uuid = '00000000-0000-0000-0000-000000000000' if CONFIG.on_prem else user_uuid
        self.setts_path = os.path.join(file_dir, setts_path)
        self.json_path = os.path.join(self.setts_path, f'{self.user_uuid}.json')
        self.app: App = App()
        self.replacements: dict[str, str] = CONFIG.Replacements.copy()
        self.pdf_params: dict = CONFIG.Pdf_params._asdict()  # noqa
        self.regex: Regex = copy(CONFIG.Regex)
        self.json_date: float = 0.0
        self.json_hash: int = 0

    def _get_hash(self) -> int:
        return hash(f'{self.app.get_values()}{self.replacements}{self.pdf_params}{self.regex}')

    @catch(SettingsError)
    def load(self) -> None:
        if not os.path.isfile(self.json_path):
            self.save()
            return

        if self.json_date == os.path.getmtime(self.json_path):
            return

        with open(file = self.json_path, mode = 'r', encoding = 'utf-8') as file:
            data = json.load(file)

        self.app = App(**data.get('app', self.app))
        self.replacements = data.get('replacements', self.replacements)
        self.pdf_params = data.get('pdf_params', self.pdf_params)
        self.regex = Regex(**data.get('regex', self.regex))

        self.json_date = os.path.getmtime(self.json_path)
        self.json_hash = self._get_hash()
        logger.info('Parsed settings')

    @catch(SettingsError)
    def save(self) -> None:
        os.makedirs(self.setts_path, exist_ok = True)
        json_hash = self._get_hash()
        if self.json_hash == json_hash:
            return

        data = {
            'app': self.app.as_dict(),
            'replacements': self.replacements,
            'pdf_params': self.pdf_params,
            'regex': self.regex._asdict(),
        }
        with open(file = self.json_path, mode = 'w', encoding = 'utf-8') as file:
            json.dump(data, file, ensure_ascii = False, indent = 4)

        self.json_date = os.path.getmtime(self.json_path)
        self.json_hash = json_hash
        logger.info('Saved settings')

    @catch(SettingsError)
    def get_proxies(self) -> dict:
        return {'http': self.app.http, 'https': self.app.https}


class App:
    __slots__ = ('dark_mode', 'show_tips', 'language', 'reformatting', 'model_name', 'http', 'https')

    def __init__(self,
                 dark_mode: bool = CONFIG.App.dark_mode,
                 show_tips: bool = CONFIG.App.show_tips,
                 language: str = CONFIG.App.language,
                 reformatting: bool = CONFIG.App.reformatting,
                 model_name: str = CONFIG.App.model_name,
                 http: str = '',
                 https: str = '') -> None:
        """
        Class wrapping for the app settings
        """
        self.dark_mode = dark_mode
        self.show_tips = show_tips
        self.language = language
        self.reformatting = reformatting
        self.model_name = model_name
        self.http = http
        self.https = https

    def as_dict(self):
        return {slot: self.__getattribute__(slot) for slot in self.__slots__}

    def get_values(self):
        return tuple(self.__getattribute__(slot) for slot in self.__slots__)
