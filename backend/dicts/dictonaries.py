import os
import json
import traceback
from uuid import UUID
from typing import Dict, Union
from backend.config.config import CONFIG, REPLACEMENTS
from backend.error.error import DictionaryError
from backend.logger.logger import logger


# TODO: write a service, which deletes all storage data after n unused days.

class Dicts(object):

    def __init__(self, folder_path: str = '.',
                 user_uuid: Union[UUID, str] = '00000000-0000-0000-0000-000000000000') -> None:
        """
        :param folder_path: path to the dictionaries folder
        :param user_uuid: user uuid to identify correspondent dictionaries
        """
        module_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), folder_path)
        self.user_uuid = user_uuid
        self.folder_path = os.path.join(module_path, 'json')
        self.replacements: Dict[str, str] = REPLACEMENTS
        self.dictionaries: Dict[str, Dict[str, str]] = {}

    def load(self, user_uuid: Union[UUID, str]) -> None:
        """
        :param user_uuid: user uuid to identify correspondent dictionaries
        """
        if CONFIG.on_prem: user_uuid = self.user_uuid
        json_path = os.path.join(self.folder_path, f'{user_uuid}.json')
        if not os.path.isfile(json_path):
            self.save(user_uuid = user_uuid)
            return
        try:
            with open(file = json_path, mode = 'r', encoding = 'utf-8') as json_file:
                data = json.load(json_file)
            self.replacements = data.get('replacements', REPLACEMENTS)
            self.dictionaries = data.get('dictionaries', {})
            logger.info('parsed dictionaries')
        except Exception:
            message = f'Could not parse json file dict with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DictionaryError(message)

    def save(self, user_uuid: Union[UUID, str]) -> None:
        """
        :param user_uuid: user uuid to identify correspondent dictionaries
        """
        try:
            if CONFIG.on_prem: user_uuid = self.user_uuid
            os.makedirs(self.folder_path, exist_ok = True)
            json_path = os.path.join(self.folder_path, f'{user_uuid}.json')
            data = {'replacements': self.replacements, 'dictionaries': self.dictionaries}
            with open(file = json_path, mode = 'w', encoding = 'utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii = False, indent = 4)
            logger.info('saved dictionaries')
        except Exception:
            message = f'Could not save json file dict with exception:\n{traceback.format_exc()}'
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
        except Exception:
            message = f'Could not parse import with exception:\n{traceback.format_exc()}'
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
        except Exception:
            message = f'Could not execute export with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DictionaryError(message)
