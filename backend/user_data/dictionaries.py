import os
import json
from uuid import UUID
from typing import Union
from backend.config.config import CONFIG
from backend.error.error import DictionaryError, catch
from backend.logger.logger import logger

file_dir = os.path.dirname(os.path.relpath(__file__))


class Dicts(object):

    def __init__(self, user_uuid: Union[UUID, str] = '00000000-0000-0000-0000-000000000000',
                 dicts_path: str = 'dicts') -> None:
        """
        :param user_uuid: user uuid to identify the corresponding dictionaries
        :param dicts_path: path to the dictionaries directory
        """
        self.user_uuid = '00000000-0000-0000-0000-000000000000' if CONFIG.on_prem else user_uuid
        self.dicts_path = os.path.join(file_dir, dicts_path)
        self.json_path: str = os.path.join(self.dicts_path, f'{self.user_uuid}.json')
        self.dictionaries: dict[str, dict[str, str]] = {}
        self.json_date: float = 0.0
        self.json_hash: int = 0
        self.dict_name: str = None

    def _get_hash(self) -> int:
        return hash(f'{self.dictionaries}')

    @catch(DictionaryError)
    def load(self) -> None:
        if not os.path.isfile(self.json_path):
            self.save()
            return

        if self.json_date == os.path.getmtime(self.json_path):
            return

        with open(file = self.json_path, mode = 'r', encoding = 'utf-8') as file:
            self.dictionaries = json.load(file)

        self.json_date = os.path.getmtime(self.json_path)
        self.json_hash = self._get_hash()
        logger.info('Parsed dictionaries')

    @catch(DictionaryError)
    def save(self) -> None:
        os.makedirs(self.dicts_path, exist_ok = True)
        json_hash = self._get_hash()
        if self.json_hash == json_hash:
            return

        with open(file = self.json_path, mode = 'w', encoding = 'utf-8') as file:
            json.dump(self.dictionaries, file, ensure_ascii = False, indent = 4)

        self.json_date = os.path.getmtime(self.json_path)
        self.json_hash = json_hash
        logger.info('Saved dictionaries')

    @catch(DictionaryError)
    def from_json_str(self, dict_name: str, data: str) -> None:
        try:
            data = json.loads(data)
            if any(not isinstance(key, str) for key in data.keys()) or \
                    any(not isinstance(val, str) for val in data.values()):
                raise DictionaryError('Found a non-string value in data')
            self.dictionaries[dict_name] = data
        except DictionaryError as exception:
            raise exception

    @catch(DictionaryError)
    def to_json_str(self, dict_name: str) -> str:
        data = self.dictionaries.get(dict_name, {})
        return json.dumps(data, ensure_ascii = False, indent = 4)
