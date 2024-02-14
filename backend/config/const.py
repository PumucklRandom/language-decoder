import os
import yaml

DECODE_COLS = [
    {'name': 'source', 'field': 'source', 'required': True, 'align': 'left'},
    {'name': 'target', 'field': 'target', 'required': True, 'align': 'left'},
]

DICT_COLS = [
    {'label': 'Source Words', 'name': 'key', 'field': 'key', 'required': True, 'sortable': True, 'align': 'left'},
    {'label': 'Target Words', 'name': 'val', 'field': 'val', 'required': True, 'sortable': True, 'align': 'left'},
]

REPLACE_COLS = [
    {'label': 'Character ', 'name': 'key', 'field': 'key', 'required': True, 'sortable': True, 'align': 'left'},
    {'label': 'Substitute', 'name': 'val', 'field': 'val', 'required': True, 'sortable': True, 'align': 'left'},
]

PDF_COLS = [
    {'name': 'key', 'field': 'key', 'required': True, 'align': 'left'},
    {'name': 'val', 'field': 'val', 'required': True, 'align': 'left'},
]
# A mapping dict to replace language independent characters for the source text
REPLACEMENTS = {'«': '"', '»': '"', '<<': '"', '>>': '"', '“': '"', '—': '-', '–': '-'}

PDF_SETTING_LABELS = [
    'Tab size',
    'Use page seperator [0, 1]',
    'Characters per line',
    'Lines per page',
    'Title font size',
    'Font size',
    'PDF width',
    'PDF block height'
]

# Character mark patterns for reformation of the source text
PUNCTUATIONS = '.!?'
BEG_PATTERNS = '#$<(\[{'
END_PATTERNS = ',;.:!?°%€>)\]}'
QUO_PATTERNS = '"\'´`'


class URLS(object):
    START = '/'
    UPLOAD = '/upload/'
    DECODING = '/decoding/'
    DICTIONARIES = '/dictionaries/'
    SETTINGS = '/settings/'
    PDF_VIEW = '/pdf-view/'
    DOWNLOAD = '/download/'


class Config(object):
    def __init__(self, config_path: str = 'config.yml'):
        config_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), config_path)
        self.load(config_path = config_path)

    def __repr__(self) -> str:
        return f'{self.__dict__}'

    def __len__(self) -> int:
        return len(self.__dict__)

    def __add__(self, other) -> None:
        self.__dict__.update(other.__dict__)

    def load(self, config_path: str) -> None:
        if not os.path.isfile(config_path):
            # TODO: Error Handling
            pass
        with open(config_path, 'r') as config_file:
            self.__dict__.update(yaml.load(config_file, yaml.FullLoader))


CONFIG = Config()

RU2DE = {
    'ICH BIN': 'Ich', 'Ich bin': 'Ich', 'ich bin': 'ich', 'ICH': 'Ich', 'DU BIST': 'Du', 'Du bist': 'Du', 'du bist': 'du',
    'ER IST': 'Er', 'Er ist': 'Er', 'er ist': 'er', 'SIE IST': 'Sie', 'Sie ist': 'Sie', 'sie ist': 'sie',
    'ES IST': 'Es', 'Es ist': 'Es', 'es ist': 'es', 'WIR SIND': 'Wir', 'Wir sind': 'Wir', 'wir sind': 'wir',
    'IHR SEID': 'Ihr', 'Ihr seid': 'Ihr', 'ihr seid': 'ihr', 'SIE SIND': 'Sie', 'Sie sind': 'Sie', 'sie sind': 'sie',
    'BIN ICH': 'Ich', 'Bin ich': 'Ich', 'bin ich': 'ich', 'BIST DU': 'Du', 'Bist du': 'Du', 'bist du': 'du',
    'IST ER': 'Er', 'Ist er': 'Er', 'ist er': 'er', 'IST SIE': 'Sie', 'Ist sie': 'Sie', 'ist sie': 'sie',
    'IST ES': 'Es', 'Ist es': 'Es', 'ist es': 'es', 'SIND WIR': 'Wir', 'Sind wir': 'Wir', 'sind wir': 'wir',
    'SEID IHR': 'Ihr', 'Seid ihr': 'Ihr', 'seid ihr': 'ihr', 'SIND SIE': 'Sie', 'Sind sie': 'Sie', 'sind sie': 'sie',
    'Für dich': 'Euch', 'für dich': 'euch', 'Dein sein': 'Euer', 'dein sein': 'euer', 'Es gibt': 'sein',
    'U': 'Bei', 'u': 'bei', 'Verfügen über': 'Bei', 'beim': 'bei', 'Beim': 'Bei', 'ZU': 'Zu', 'Zu': 'zu', 'IN': 'In', 'V': 'In',
    'v': 'in', 'Ö': 'über', 'ö': 'über', 'UND': 'Und', 'EIN': 'Und', 'ABER': 'Und', 'MIT': 'Mit', 'Mit': 'mit', 'Pro': 'Für',
    'pro': 'für', 'von diesen': 'diese', 'BEI': 'In', 'ABER)': 'A)', 'BEIM': 'In', 'Std': 'Stunde', 'Std.': 'Stunde',
    'Auf der': 'Auf', 'auf der': 'auf', 'Jede einzelne': 'Jede', 'jede einzelne': 'jede', 'Sie sagen': 'sprechen',
    'tun': 'machen', 'Tun': 'machen', 'tut': 'macht', 'Tut': 'macht', 'tat': 'machte', 'Tat': 'machte', 'co': 'mit', 'Co': 'Mit'
}
