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
    The LanguageDecoder is used to translate a text from a source language to a given target language word by word (decoding).
    Therefor the Google translator is used to generate a decoded text file.
    After checking the decoded text file, the decoding can be converted to a pdf file.
    """

    def __init__(self,
                 uuid: Union[UUID, str] = '00000000-0000-0000-0000-000000000000',
                 source_language: str = 'auto',
                 target_language: str = 'english',
                 dict_name: str = '',
                 punctuations: str = PUNCTUATIONS,
                 beg_patterns: str = BEG_PATTERNS,
                 end_patterns: str = END_PATTERNS,
                 quo_patterns: str = QUO_PATTERNS,
                 new_line: str = '\n',
                 word_space: int = 4,
                 char_lim_decode: int = 120) -> None:

        """
        :param uuid: user uuid to identify correspondent dictionaries
        :param source_language: the translation source language
        :param target_language: the translation target language
        :param dict_name: the name of the  dictionary to select the desires dictionary
        :param punctuations: character patterns at the end of a sentence
        :param beg_patterns: character patterns at the beginning of a word
        :param end_patterns: character patterns at the end of a word
        :param quo_patterns: character patterns for quotations
        :param new_line: new line string
        :param word_space: the space between two words
        :param char_lim_decode: character limit of one line for decode text file
        source_words: list of all source words
        decode_words: list of all decoded words
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
        self.word_space = word_space
        self.char_lim_decode = char_lim_decode
        self.source_path = ''
        self.source_text = ''
        self.source_words = []
        self.decoded_words = []
        self.decoded_text = ''
        self.translated_text = ''

    def get_supported_languages(self, show: bool = False) -> List[str]:
        languages = self._translator.get_supported_languages(as_dict = True)
        if show:
            self._pp.pprint(languages.keys())
        return list(languages.keys())

    def set_languages(self) -> None:
        self._translator.source = self.source_language
        self._translator.target = self.target_language

    def translate(self, text: str) -> str:
        try:
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

    def translate_batch(self, batch: List[str]) -> List[str]:
        try:
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
    def _get_decode_paths(source_path: str) -> Tuple[str, str]:
        if not os.path.isfile(source_path):
            raise OSError('Error in `LanguageDecoder´. Text file not Found.')
        title = os.path.basename(source_path).split('.')[0]
        decode_path = os.path.join(os.path.dirname(source_path), f'{title}_decode.txt')
        transl_path = os.path.join(os.path.dirname(source_path), f'{title}_transl.txt')
        return decode_path, transl_path

    @staticmethod
    def delete_decoded_files(decode_path: str) -> None:
        transl_path = decode_path.replace('decode.txt', 'transl.txt')
        if os.path.isfile(decode_path):
            os.remove(decode_path)
        if os.path.isfile(transl_path):
            os.remove(transl_path)

    def _read_text(self, source_path: str) -> None:
        if source_path:
            self.source_path = source_path
            decode_path, _ = self._get_decode_paths(source_path = source_path)
            if os.path.isfile(decode_path):
                # print(f'Text already decoded: `{decode_path}´. \n')
                self.source_text = ''
                return
            try:
                with open(file = source_path, mode = 'r', encoding = 'utf-8') as file:
                    self.source_text = file.read()
            except IOError as e:
                # TODO: Error handling and logger
                self.source_text = ''
                return
            print(f'Decode Text for: `{source_path}´.')

    @staticmethod
    def replace_words(word_list: List[str], dictionary: dict) -> List[str]:
        return [dictionary.get(word) if word in dictionary.keys() else word for word in word_list]

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
        self._dicts.load(uuid = self.uuid)
        # remove redundant whitespaces and new lines
        text = ' '.join(text.split())
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
        return ' '.join(text.split())

    def _strip_word(self, source_word: str, decode_word: str) -> str:
        decode_word = source_word if decode_word is None else decode_word
        # get the number of marks in the beginning of the word
        re_com = re.compile(f'^[{self.beg_patterns + self.quo_patterns}]*')
        beg_num = len(re.search(re_com, decode_word).group())
        # get the number of marks in the end of the word
        re_com = re.compile(f'[{self.end_patterns + self.quo_patterns}]*$')
        end_num = len(re.search(re_com, decode_word).group())
        # if the end numbers are 0 get the length of the words
        end_num = -len(decode_word) if end_num == 0 else end_num
        # return target word without marks
        return decode_word[beg_num:-end_num]

    def _wrap_word(self, source_word: str, decode_word: str) -> str:
        # get the number of marks in the beginning of the word
        re_com = re.compile(f'^[{self.beg_patterns + self.quo_patterns}]*')
        beg_num = len(re.search(re_com, source_word).group())
        # get the number of marks in the end of the word
        re_com = re.compile(f'[{self.end_patterns + self.quo_patterns}]*$')
        end_num = len(re.search(re_com, source_word).group())
        # if the end numbers are 0 get the length of the words
        end_num = -len(source_word) if end_num == 0 else end_num
        # add the marks from source word to target word
        return f'{source_word[0:beg_num]}{decode_word}{source_word[-end_num:]}'

    def split_text(self) -> None:
        if len(self.source_text) == 0:
            # TODO: Error handling and logger
            print('Source text is empty.\n')
            raise Exception
        # reformat text for translator
        source_text = self._reformat_text(text = self.source_text)
        # split text into words
        self.source_words = source_text.split()

    def decode_words(self):
        print(f'Decode {len(self.source_words)} words.')
        decode_words = self.translate_batch(self.source_words)
        if len(decode_words) != len(self.source_words):
            # TODO: Error handling and logger
            print('Something went wrong with the translation.\n')
            raise Exception
        self.decoded_words.clear()
        for source_word, decode_word in zip(self.source_words, decode_words):
            # first strip the decode words from marks
            decode_word = self._strip_word(source_word = source_word, decode_word = decode_word)
            # then add missing marks from source words to decode words
            self.decoded_words.append(self._wrap_word(source_word = source_word, decode_word = decode_word))
        print(f'Decoded words!\n')
        return self.decoded_words

    def apply_dict(self) -> None:
        self._dicts.load(uuid = self.uuid)
        dictionary = self._dicts.dictionaries.get(self.dict_name)
        decode_words = []
        for source_word, decode_word in zip(self.source_words, self.decoded_words):
            # first strip the decode words from marks
            decode_words.append(self._strip_word(source_word = source_word, decode_word = decode_word))
        # replace words from dictionary
        decode_words = self.replace_words(word_list = decode_words, dictionary = dictionary)
        self.decoded_words.clear()
        for source_word, decode_word in zip(self.source_words, decode_words):
            # add missing marks from source words to decode words
            self.decoded_words.append(self._wrap_word(source_word = source_word, decode_word = decode_word))

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
        decode_line = ''
        self.decoded_text = ''
        for source_word, decode_word in zip(self.source_words, self.decoded_words):
            # get the length of the longest word + word_space
            word_len = utils.lonlen([source_word, decode_word]) + self.word_space
            # get the length of the current line
            line_len += word_len
            # if the length of the line is too long
            if (line_len - self.word_space) > self.char_lim_decode:
                # add self.new_line at the end
                source_line = f'{source_line[0:-self.word_space]}{self.new_line}'
                decode_line = f'{decode_line[0:-self.word_space]}{self.new_line}'
                # combine to formatted text
                self.decoded_text = f'{self.decoded_text}{source_line}{decode_line}{self.new_line}'
                # set length to word length
                line_len = word_len
                # adjust word for same length, add word_space and add it to the line
                source_line = source_word.ljust(word_len, ' ')
                decode_line = decode_word.ljust(word_len, ' ')
            # if a punctuation mark is at the end of the word (end of sentence)
            elif any(punctuation in source_word for punctuation in PUNCTUATIONS):
                # add word to the line and add self.new_line at the end
                source_line = f'{source_line}{source_word}{self.new_line}'
                decode_line = f'{decode_line}{decode_word}{self.new_line}'
                # combine to formatted text
                self.decoded_text = f'{self.decoded_text}{source_line}{decode_line}{self.new_line}'
                # reset length and lines
                line_len = 0
                source_line = ''
                decode_line = ''
            else:
                # adjust word for same length, add word_space and add it to the line
                source_line += source_word.ljust(word_len, ' ')
                decode_line += decode_word.ljust(word_len, ' ')
        # if the loop is finished add the last lines
        source_line = f'{source_line[0:-self.word_space]}{self.new_line}'
        decode_line = f'{decode_line[0:-self.word_space]}{self.new_line}'
        self.decoded_text = f'{self.decoded_text}{source_line}{decode_line}{self.new_line}'

        self.save_decoded_text()
        if translate:
            self.translate_text()
            self.save_translated_text()

    def save_decoded_text(self) -> str:
        decode_path, _ = self._get_decode_paths(source_path = self.source_path)
        if not os.path.isfile(decode_path) and self.decoded_text:
            with open(file = decode_path, mode = 'w', encoding = 'utf-8') as file:
                file.write(self.decoded_text)
            return decode_path

    def translate_text(self) -> None:
        self.translated_text = self.translate(self.source_text)
        self.translated_text = textwrap.fill(self.translated_text, width = self.char_lim_decode)

    def save_translated_text(self) -> str:
        _, transl_path = self._get_decode_paths(source_path = self.source_path)
        if not os.path.isfile(transl_path) and self.translated_text:
            with open(file = transl_path, mode = 'w', encoding = 'utf-8') as file:
                file.write(self.translated_text)
            return transl_path
