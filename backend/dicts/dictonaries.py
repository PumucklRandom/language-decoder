import os
import json
from uuid import UUID
from typing import Dict, Union


class Dicts(object):

    def __init__(self, folder_path: str = '.') -> None:
        """
        replace_dict: a dictionary to replace chars in source text
        dictionaries: a dictionary of dictionaries to correct language dependent translation mistakes
        """
        self.folder_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), folder_path)
        self.replacements: Dict[str, str] = {}
        self.dictionaries: Dict[str, Dict[str, str]] = {}

    def load(self, uuid: Union[UUID, str]) -> None:
        """
        :param uuid: user uuid to identify correspondent dictionaries
        """
        json_path = os.path.join(self.folder_path, f'{uuid}.json')
        if os.path.isfile(json_path):
            with open(file = json_path, mode = 'r') as json_file:
                data = json.load(json_file)
            self.replacements = data.get('replacements')
            self.dictionaries = data.get('dictionaries')
        else:
            with open(file = json_path, mode = 'w') as json_file:
                data = {'replacements': {}, 'dictionaries': {}}
                json.dump(data, json_file, indent = 4)

    def save(self, uuid: Union[UUID, str]) -> None:
        """
        :param uuid: user uuid to identify correspondent dictionaries
        """
        json_path = os.path.join(self.folder_path, f'{uuid}.json')
        with open(file = json_path, mode = 'w') as json_file:
            data = {'replacements': self.replacements, 'dictionaries': self.dictionaries}
            json.dump(data, json_file, indent = 4)
