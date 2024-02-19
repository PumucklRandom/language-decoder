import os
import re
import textwrap
from uuid import UUID
from typing import Tuple, List, Union
from pprint import PrettyPrinter
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError, TooManyRequests, MicrosoftAPIerror
from backend.config.const import PUNCTUATIONS, BEG_PATTERNS, END_PATTERNS, QUO_PATTERNS
from backend.dicts.dictonaries import Dicts
from backend.utils import utilities as utils

PACKAGE_PATH = os.path.dirname(os.path.relpath(__file__))


class LanguageDecoder(object):
    """
    The LanguageDecoder translates a given source language to a desired target language word by word (decoding).
    Therefor the Google translator is used to generate a decoded text file.
    After checking the decoded text file, the decoding can be converted to a pdf file.
    """

    def __init__(self,
                 uuid: Union[UUID, str] = '00000000-0000-0000-0000-000000000000',
                 source_language: str = 'auto',
                 target_language: str = 'english',
                 dict_name: str = None,
                 punctuations: str = PUNCTUATIONS,
                 beg_patterns: str = BEG_PATTERNS,
                 end_patterns: str = END_PATTERNS,
                 quo_patterns: str = QUO_PATTERNS,
                 new_line: str = '\n',
                 tab_size: int = 4,
                 char_lim: int = 120) -> None:

        """
        :param uuid: user uuid to identify correspondent dictionaries
        :param source_language: the translation source language
        :param target_language: the translation target language
        :param dict_name: the name of the dictionary to select the desires dictionary
        :param punctuations: character patterns at the end of a sentence
        :param beg_patterns: character patterns at the beginning of a word
        :param end_patterns: character patterns at the end of a word
        :param quo_patterns: character patterns for quotations
        :param new_line: new line string
        :param tab_size: the tab size between two words
        :param char_lim: character limit of one line
        """

        self._pp = PrettyPrinter(indent = 4)
        self._translator = GoogleTranslator(source = source_language, target = target_language)
        self._dicts = Dicts()
        self.uuid = uuid
        self.source_language = source_language
        self.target_language = target_language
        self.dict_name = dict_name
        self.punctuations = punctuations
        self.beg_patterns = beg_patterns
        self.end_patterns = end_patterns
        self.quo_patterns = quo_patterns
        self.new_line = new_line
        self.tab_size = tab_size
        self.char_lim = char_lim
        self.source_path = ''
        self.source_text = ''
        self.decode_text = ''
        self.source_words = []
        self.target_words = []
        self.translated_text = ''
        self.title = ''

    def get_supported_languages(self, show: bool = False) -> List[str]:
        languages = self._translator.get_supported_languages(as_dict = True)
        if show:
            self._pp.pprint(languages.keys())
        return list(languages.keys())

    def _set_languages(self) -> None:
        self._translator.source = self.source_language
        self._translator.target = self.target_language

    def _translate(self, text: str) -> str:
        try:
            self._set_languages()
            return self._translator.translate(text)
        except RequestError as exception:
            print('Connection Error')
            print(exception)
        except TooManyRequests as exception:
            print('To Many Requests')
            print(exception)
        except MicrosoftAPIerror as exception:
            print('Microsoft API Error')
            print(exception)
        except Exception as exception:
            print('Unexpected Error')
            print(exception)
            return ''

    def _translate_batch(self, batch: List[str]) -> List[str]:
        try:
            self._set_languages()
            return self._translator.translate_batch(batch)
        except RequestError as exception:
            print('Connection Error')
            print(exception)
        except TooManyRequests as exception:
            print('To Many Requests')
            print(exception)
        except MicrosoftAPIerror as exception:
            print('Microsoft API Error')
            print(exception)
        except Exception as exception:
            print('Unexpected Error')
            print(exception)
            return ['']

    @staticmethod
    def _get_destin_paths(source_path: str) -> Tuple[str, str]:
        if not os.path.isfile(source_path):
            raise OSError('Error in `LanguageDecoder´. Text file not Found.')
        title = os.path.basename(source_path).split('.')[0]
        destin_path = os.path.join(os.path.dirname(source_path), f'{title}_decode.txt')
        transl_path = os.path.join(os.path.dirname(source_path), f'{title}_transl.txt')
        return destin_path, transl_path

    @staticmethod
    def delete_decoded_files(destin_path: str) -> None:
        transl_path = destin_path.replace('decode.txt', 'transl.txt')
        if os.path.isfile(destin_path):
            os.remove(destin_path)
        if os.path.isfile(transl_path):
            os.remove(transl_path)

    def _read_text(self, source_path: str) -> None:
        if source_path:
            self.source_path = source_path
            destin_path, _ = self._get_destin_paths(source_path = source_path)
            if os.path.isfile(destin_path):
                # print(f'Text already decoded: `{destin_path}´. \n')
                self.source_text = ''
                return
            try:
                with open(file = source_path, mode = 'r', encoding = 'utf-8') as file:
                    self.source_text = file.read()
            except IOError:
                # TODO: Error handling and logger
                self.source_text = ''
                return
            print(f'Decode Text for: `{source_path}´.')

    @staticmethod
    def _split_camel_case(text: str) -> str:
        # 'camelCase' -> 'camel. Case'
        i = 0
        end = len(text) - 1
        while i < end:
            if text[i].islower() and text[i + 1].isupper():
                text = f'{text[:i + 1]}. {text[i + 1:]}'
                i += 2
                end += 2
            i += 1
        return text

    def _reformat_text(self, text: str) -> str:
        text = ' '.join(text.split())
        self._dicts.load(uuid = self.uuid)
        # replace special characters with common ones
        for chars in self._dicts.replacements.keys():
            text = text.replace(chars, self._dicts.replacements.get(chars))
        # swap "quotation marks" with punctuations if quotation mark is followed by punctuation
        text = re.sub(f'([{self.quo_patterns}])\s*([{self.punctuations}])', r'\2\1', text)
        # remove any white whitespaces after "begin marks" and add one whitespace before "begin marks"
        text = re.sub(f'([{self.beg_patterns}])\s*', r' \1', text)
        # remove any white whitespaces before "end marks" and add one whitespace after "end marks"
        text = re.sub(f'\s*([{self.end_patterns}])', r'\1 ', text)
        # remove whitespaces inside "quotation mark" pairs and add whitespaces outside of pairs
        text = re.sub(f'([{self.quo_patterns[0]}])\s*(.*?)\s*([{self.quo_patterns[0]}])', r' \1\2\3 ', text)
        text = re.sub(f'([{self.quo_patterns[1]}])\s*(.*?)\s*([{self.quo_patterns[1]}])', r' \1\2\3 ', text)
        text = re.sub(f'([{self.quo_patterns[2:]}])\s*(.*?)\s*([{self.quo_patterns[2:]}])', r' \1\2\3 ', text)
        # add potentially missing dots
        text = self._split_camel_case(text)
        # add a dot at the end of the text in case of missing punctuation
        if not any(punctuation in text.split()[-1] for punctuation in PUNCTUATIONS):
            text += '.'
        # remove redundant whitespaces and new lines
        return ' '.join(text.split())

    @staticmethod
    def _strip_word(target_word: str) -> str:
        # remove all non-alphanumeric and non-minus characters
        return re.sub('[^-\w]*', '', target_word)

    def _wrap_word(self, source_word: str, target_word: str) -> str:
        # make sure target word is stripped
        target_word = self._strip_word(target_word)
        # get marks at the beginning of the word
        beg = re.search('^\W*', source_word).group()
        # get marks at the end of the word
        end = re.search('\W*$', source_word).group()
        return f'{beg}{target_word}{end}'

    def split_text(self) -> None:
        if len(self.source_text) == 0:
            # TODO: Error handling and logger
            print('Source text is empty.\n')
            raise Exception
        # reformat text for translator
        source_text = self._reformat_text(text = self.source_text)
        # split text into words
        self.source_words = source_text.split()

    def decode_words(self) -> None:
        print(f'Decode {len(self.source_words)} words.')
        target_words = self._translate_batch(self.source_words)
        if len(target_words) != len(self.source_words):
            # TODO: Error handling and logger
            print('Something went wrong with the translation.\n')
            raise Exception
        self.target_words.clear()
        for source_word, target_word in zip(self.source_words, target_words):
            # take source word if target word is None
            target_word = source_word if target_word is None else target_word
            # add missing marks from source word to target word
            self.target_words.append(self._wrap_word(source_word = source_word, target_word = target_word))
        print('Decoded words!\n')

    def apply_dict(self) -> None:
        if not self.dict_name:
            return
        self._dicts.load(uuid = self.uuid)
        dictionary = self._dicts.dictionaries.get(self.dict_name, {})
        target_words = self.target_words.copy()
        self.target_words.clear()
        for source_word, target_word in zip(self.source_words, target_words):
            # first strip the source word for the dictionary keys
            source_strip = self._strip_word(target_word = source_word)
            if source_strip in dictionary.keys():
                # replace target word if stripped source word is key
                target_word = dictionary.get(source_strip)
            # add missing marks from source word to target word
            self.target_words.append(self._wrap_word(source_word = source_word, target_word = target_word))

    def decode_text_to_file(self, source_path: str = None, translate: bool = False) -> None:
        try:
            self._read_text(source_path = source_path)
            self.split_text()
            self.decode_words()
            self.apply_dict()
        except Exception:
            return
        # formatting text
        line_len = 0
        source_line = ''
        target_line = ''
        self.decode_text = ''
        for source_word, target_word in zip(self.source_words, self.target_words):
            # get the length of the longest word + word_space
            word_len = utils.lonlen([source_word, target_word]) + self.tab_size
            # get the length of the current line
            line_len += word_len
            # if the length of the line is too long
            if (line_len - self.tab_size) > self.char_lim:
                # add self.new_line at the end
                source_line = f'{source_line[0:-self.tab_size]}{self.new_line}'
                target_line = f'{target_line[0:-self.tab_size]}{self.new_line}'
                # combine to formatted text
                self.decode_text = f'{self.decode_text}{source_line}{target_line}{self.new_line}'
                # set length to word length
                line_len = word_len
                # adjust word for same length, add word_space and add it to the line
                source_line = source_word.ljust(word_len, ' ')
                target_line = target_word.ljust(word_len, ' ')
            # if a punctuation mark is at the end of the word (end of sentence)
            elif any(punctuation in source_word for punctuation in PUNCTUATIONS):
                # add word to the line and add self.new_line at the end
                source_line = f'{source_line}{source_word}{self.new_line}'
                target_line = f'{target_line}{target_word}{self.new_line}'
                # combine to formatted text
                self.decode_text = f'{self.decode_text}{source_line}{target_line}{self.new_line}'
                # reset length and lines
                line_len = 0
                source_line = ''
                target_line = ''
            else:
                # adjust word for same length, add word_space and add it to the line
                source_line += source_word.ljust(word_len, ' ')
                target_line += target_word.ljust(word_len, ' ')
        # if the loop is finished add the last lines
        source_line = f'{source_line[0:-self.tab_size]}{self.new_line}'
        target_line = f'{target_line[0:-self.tab_size]}{self.new_line}'
        self.decode_text = f'{self.decode_text}{source_line}{target_line}{self.new_line}'

        self._save_decode_text()
        if translate:
            self._translate_text()
            self._save_translated_text()

    def _save_decode_text(self) -> str:
        destin_path, _ = self._get_destin_paths(source_path = self.source_path)
        if not os.path.isfile(destin_path) and self.decode_text:
            with open(file = destin_path, mode = 'w', encoding = 'utf-8') as file:
                file.write(self.decode_text)
            return destin_path

    def _translate_text(self) -> None:
        self.translated_text = self._translate(self.source_text)
        self.translated_text = textwrap.fill(self.translated_text, width = self.char_lim)

    def _save_translated_text(self) -> str:
        _, transl_path = self._get_destin_paths(source_path = self.source_path)
        if not os.path.isfile(transl_path) and self.translated_text:
            with open(file = transl_path, mode = 'w', encoding = 'utf-8') as file:
                file.write(self.translated_text)
            return transl_path
