import os
import json
from uuid import UUID
from typing import Dict, Union
from backend.config.config import REPLACEMENTS
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
        json_path = os.path.join(self.folder_path, f'{uuid}.json')
        if os.path.isfile(json_path):
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

        else:
            self.save(uuid = uuid)

    def save(self, uuid: Union[UUID, str]) -> None:
        """
        :param uuid: user uuid to identify correspondent dictionaries
        """
        try:
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
