import os
import json
from uuid import UUID
from typing import Dict, Union
from backend.config.config import CONFIG, REPLACEMENTS
from backend.error.error import DictionaryError
from backend.logger.logger import logger


class Dicts(object):

    def __init__(self, folder_path: str = '.') -> None:
        """
        replace_dict: a dictionary to replace chars in source text
        dictionaries: a dictionary of dictionaries to correct language dependent translation mistakes
        """
        module_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), folder_path)
        self.folder_path = os.path.join(module_path, 'json')
        self.replacements: Dict[str, str] = REPLACEMENTS
        self.dictionaries: Dict[str, Dict[str, str]] = {}

    def load(self, uuid: Union[UUID, str]) -> None:
        """
        :param uuid: user uuid to identify correspondent dictionaries
        """
        if CONFIG.on_prem:
            uuid = '00000000-0000-0000-0000-000000000000'
        json_path = os.path.join(self.folder_path, f'{uuid}.json')
        if not os.path.isfile(json_path):
            self.save(uuid = uuid)
            return
        try:
            with open(file = json_path, mode = 'r', encoding = 'utf-8') as json_file:
                data = json.load(json_file)
            self.replacements = data.get('replacements', REPLACEMENTS)
            self.dictionaries = data.get('dictionaries', {})
            logger.info('parsed dictionaries')
        except Exception as exception:
            message = f'Could not parse json file dict with exception:\n{exception}'
            logger.error(message)
            raise DictionaryError(message)

    def save(self, uuid: Union[UUID, str]) -> None:
        """
        :param uuid: user uuid to identify correspondent dictionaries
        """
        try:
            if CONFIG.on_prem:
                uuid = '00000000-0000-0000-0000-000000000000'
            os.makedirs(self.folder_path, exist_ok = True)
            json_path = os.path.join(self.folder_path, f'{uuid}.json')
            data = {'replacements': self.replacements, 'dictionaries': self.dictionaries}
            with open(file = json_path, mode = 'w', encoding = 'utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii = False, indent = 4)
            logger.info('saved dictionaries')
        except Exception as exception:
            message = f'Could not save json file dict with exception:\n{exception}'
            logger.error(message)
            raise DictionaryError(message)

    def import_(self, dict_name: str, data: str) -> None:
        try:
            data = json.loads(data)
            if any(not isinstance(key, str) for key in data.keys()) or \
                    any(not isinstance(val, str) for val in data.values()):
                raise DictionaryError('Found a non-string value in data')
            self.dictionaries[dict_name] = data
        except DictionaryError as exception:
            raise exception
        except Exception as exception:
            message = f'Could not parse import with exception:\n{exception}'
            logger.error(message)
            raise DictionaryError(message)

    def export(self, dict_name: str, destin_path: str = '') -> str:
        try:
            data = self.dictionaries.get(dict_name, {})
            data_str = json.dumps(data, ensure_ascii = False, indent = 4)
            if not destin_path:
                return data_str
            title = os.path.basename(destin_path).split('.')[0]
            path = os.path.join(os.path.dirname(destin_path), f'{title}.json')
            with open(file = path, mode = 'w', encoding = 'utf-8') as file:
                file.write(data_str)
        except Exception as exception:
            message = f'Could not execute export with exception:\n{exception}'
            logger.error(message)
            raise DictionaryError(message)
