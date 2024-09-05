import os
import re
import json
import textwrap
import requests
import traceback
from uuid import UUID
from typing import Tuple, List, Union
from pprint import PrettyPrinter
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError, TooManyRequests, TranslationNotFound
from backend.config.config import CONFIG, Config
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.dicts.dictonaries import Dicts
from backend.utils import utilities as utils


# PACKAGE_PATH = os.path.dirname(os.path.relpath(__file__))


class LanguageDecoder(object):
    """
    The LanguageDecoder translates a given source language to a desired target language word by word (decoding).
    Therefor the Google translator is used to generate a decoded text file.
    After checking the decoded text file, the decoding can be converted to a pdf file.
    """

    def __init__(self,
                 user_uuid: Union[UUID, str] = '00000000-0000-0000-0000-000000000000',
                 source_language: str = 'auto',
                 target_language: str = 'english',
                 dict_name: str = None,
                 new_line: str = '\n',
                 tab_size: int = 4,
                 char_lim: int = 120,
                 proxies: dict = None,
                 regex: Config.Regex = CONFIG.Regex) -> None:

        """
        :param user_uuid: user uuid to identify correspondent dictionaries
        :param source_language: the translation source language
        :param target_language: the translation target language
        :param dict_name: the name of the dictionary to select the desires dictionary
        :param new_line: new line string
        :param tab_size: the tab size between two words
        :param char_lim: character limit of one line
        :param proxies: set proxies for translator
        :param regex: a set of character patterns for regex compilations
        """

        self._pp = PrettyPrinter(indent = 4)
        self.user_uuid = user_uuid
        self.source_language = source_language
        self.target_language = target_language
        self.dict_name = dict_name
        self.proxies = proxies
        self._dicts = Dicts(user_uuid = self.user_uuid)
        self._translator = self.__init_translator__()
        self.regex = regex
        self.new_line = new_line
        self.tab_size = tab_size
        self.char_lim = char_lim
        self.source_path: str = ''
        self.reformatting: bool = True

    def __init_translator__(self) -> GoogleTranslator:
        self._translator = GoogleTranslator(
            source = self.source_language,
            target = self.target_language,
            proxies = self.proxies)
        return self._translator

    def get_supported_languages(self, show: bool = False) -> List[str]:
        try:
            languages = self._translator.get_supported_languages(as_dict = True)
            if show: self._pp.pprint(languages.keys())
            return list(languages.keys())
        except Exception:
            message = f'Could not fetch supported languages with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    def translate_source(self, source: Union[List[str], str]) -> Union[List[str], str]:
        try:
            self.__init_translator__()
            if isinstance(source, list):
                return self._translator.translate_batch(source)
            elif isinstance(source, str):
                return self._translator.translate(source)
        except TooManyRequests:
            message = 'Too many requests! Try again later!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise DecoderError(message)
        except RequestError:
            message = 'Request Error! Check your internet connection or your proxy settings!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise DecoderError(message)
        except requests.exceptions.ProxyError:
            message = 'Request Error! Check your proxy settings!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise DecoderError(message)
        except TranslationNotFound:
            message = 'Translator Error!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise DecoderError(message)
        except Exception:
            message = 'Unexpected Error!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise Exception(message)

    @staticmethod
    def _split_camel_case(text: str) -> str:
        # 'camelCase' -> 'camel. Case'
        return re.sub('([a-z])([A-Z])', r'\1. \2', text)

    def _reformat_text(self, text: str) -> str:
        try:
            # remove new lines and add space at the end of text for regex
            text = ' '.join(text.split()) + ' '
            self._dicts.load(user_uuid = self.user_uuid)
            # replace special characters with common ones
            for chars in self._dicts.replacements.keys():
                text = text.replace(chars, self._dicts.replacements.get(chars))
            # swap quotes/brackets with punctuations if quotes/brackets are followed by punctuation
            text = re.sub(f'([{self.regex.quotes}{self.regex.close}])\s*([{self.regex.puncts}])', r'\2\1', text)
            # remove any white whitespaces after "begin marks" and add one whitespace before "begin marks"
            text = re.sub(f'([{self.regex.begins}{self.regex.opens}])\s*', r' \1', text)
            # remove any white whitespaces before "ending marks" and add one whitespace after "ending marks"
            text = re.sub(f'\s*([{self.regex.ending}{self.regex.close}])', r'\1 ', text)
            # remove any white whitespaces before "digit marks" and
            #   if "digit marks" are not followed by digits add one whitespace after "digit marks"
            text = re.sub(f'\s*([{self.regex.digits}])(\D)', r'\1 \2', text)
            # remove any whitespaces inside quote pairs and add one whitespaces outside of quote pairs
            for quote in self.regex.quotes:
                text = re.sub(f'([{quote}])\s*(.*?)\s*([{quote}])', r' \1\2\3 ', text)
            # add potentially missing dots
            text = self._split_camel_case(text)
            # remove redundant whitespaces
            text = ' '.join(text.split())
            # add a dot at the end of the text in case of missing punctuation
            if not any(punctuation in text.split()[-1] for punctuation in self.regex.puncts):
                text += '.'
            return text
        except Exception:
            message = f'Could not reformat source text with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    @staticmethod
    def _strip_word(word: str) -> str:
        # remove all non-alphanumeric and non-minus characters
        return re.sub('\A[\W_]*|[^\w\s_-]*|[\W_]*\Z', '', word)

    def _wrap_word(self, source_word: str, target_word: str) -> str:
        # make sure target word is stripped
        target_word = self._strip_word(target_word)
        # check source word for all not alphanumeric
        if all(not char.isalnum() for char in source_word):
            return source_word
        # get marks at the beginning of the word
        beg = re.search('\A[\W_]*', source_word).group()
        # get marks at the end of the word
        end = re.search('[\W_]*\Z', source_word).group()
        return f'{beg}{target_word}{end}'

    def _split_sentences(self, text: str) -> List[str]:
        # spit text into sentences with consideration of quotes and brackets
        return re.findall(f'(.*?[{self.regex.puncts}][{self.regex.close}{self.regex.quotes}]?)\s+', f'{text} ')

    def decode_sentences(self, source_words: List[str]) -> List[str]:
        text = ' '.join(source_words)
        if not any(punctuation in text.split()[-1] for punctuation in self.regex.puncts):
            text += '.'
        scr_sentences = self._split_sentences(text = text)
        tar_sentences = self.translate_source(scr_sentences)
        sentences = list()
        for source, target in zip(scr_sentences, tar_sentences):
            sentences.extend([source, target, '/N'])
        sentences.pop(-1)
        return sentences

    @staticmethod
    def find_replace(source_words: List[str], target_words: List[str],
                     find: str, repl: str) -> Tuple[List[str], List[str]]:
        for i, (source, target) in enumerate(zip(source_words, target_words)):
            source_words[i] = source.replace(find, repl)
            target_words[i] = target.replace(find, repl)
        return source_words, target_words

    def split_text(self, source_text: str) -> List[str]:
        try:
            if len(source_text) == 0:
                message = 'Source Text is empty'
                logger.error(message)
                raise DecoderError(message)
            # reformat text for translator
            if self.reformatting:
                source_text = self._reformat_text(text = source_text)
            else:
                source_text = ' '.join(source_text.split())
            # split text into words
            return source_text.split()
        except Exception:
            message = f'Could not split source text with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    def decode_words(self, source_words: List[str]) -> List[str]:
        try:
            logger.info(f'Decode {len(source_words)} words.')
            # strip source words before translation
            source_words_strip = list(map(self._strip_word, source_words))
            target_words_strip = self.translate_source(source_words_strip)
            if len(target_words_strip) != len(source_words):
                message = 'Length mismatch between source words and target words'
                logger.error(message)
                raise DecoderError(message)
            target_words = list()
            for source_word, target_word in zip(source_words, target_words_strip):
                # take source word if target word is None
                target_word = source_word if target_word is None else target_word
                # add missing marks from source word to target word
                target_words.append(self._wrap_word(source_word = source_word, target_word = target_word))
            logger.info('Decoded words.')
            return target_words
        except Exception:
            message = f'Could not decode source words with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    def apply_dict(self, source_words: List[str], target_words: List[str]) -> List[str]:
        try:
            if not self.dict_name:
                return target_words
            self._dicts.load(user_uuid = self.user_uuid)
            dictionary = self._dicts.dictionaries.get(self.dict_name, {})
            target_words_copy = target_words.copy()
            target_words.clear()
            for source_word, target_word in zip(source_words, target_words_copy):
                # first strip the source word for the dictionary keys
                source_strip = self._strip_word(source_word)
                if source_strip in dictionary.keys():
                    # replace target word if stripped source word is key
                    target_word = dictionary.get(source_strip)
                # add missing marks from source word to target word
                target_words.append(self._wrap_word(source_word = source_word, target_word = target_word))
            return target_words
        except Exception:
            message = f'Could not apply dictionary with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    @staticmethod
    def import_(data: str) -> Tuple[List[str], List[str], List[str]]:
        try:
            data = json.loads(data)
            if len(data.get('source', [])) != len(data.get('target', [])):
                raise DecoderError('Unequal number of source and target words')
            if any(not isinstance(scr, str) for scr in data.get('source', [])) or \
                    any(not isinstance(tar, str) for tar in data.get('target', [])):
                raise DecoderError('Found a non-string value in data')
            source_words = data.get('source', [])
            target_words = data.get('target', [])
            sentences = []
            if all(isinstance(sentence, str) for sentence in data.get('sentences', [])):
                sentences = data.get('sentences', [])
            return source_words, target_words, sentences
        except DecoderError as exception:
            raise exception
        except Exception:
            message = f'Could not parse import with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    @staticmethod
    def export(source_words: List[str], target_words: List[str],
               sentences: List[str], destin_path: str = '') -> str:
        try:
            data = {'source': source_words, 'target': target_words, 'sentences': sentences}
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
            raise DecoderError(message)

    ####################################################################################################
    # Methods for backend only
    ####################################################################################################

    @staticmethod
    def _get_destin_paths(source_path: str) -> Tuple[str, str]:
        if not os.path.isfile(source_path):
            message = f'Text file not found at "{source_path}"'
            logger.error(message)
            raise DecoderError(message)
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

    def _read_text(self, source_path: str) -> str:
        try:
            if source_path:
                self.source_path = source_path
                destin_path, _ = self._get_destin_paths(source_path = source_path)
                if os.path.isfile(destin_path):
                    # logger.info(f'Text already decoded at: "{destin_path}"')
                    return ''
                try:
                    with open(file = source_path, mode = 'r', encoding = 'utf-8') as file:
                        source_text = file.read()
                except IOError:
                    message = f'Could not open file at "{source_path}" with exception:\n{traceback.format_exc()}'
                    logger.error(message)
                    raise DecoderError(message)
            logger.info(f'Decode Text for: "{source_path}".')
            return source_text
        except Exception:
            message = f'Could not read text file with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    def decode_text_to_file(self, source_path: str = None, translate: bool = False) -> None:
        try:
            source_text = self._read_text(source_path = source_path)
            if not source_text: return
            source_words = self.split_text(source_text = source_text)
            target_words = self.decode_words(source_words = source_words)
            target_words = self.apply_dict(source_words = source_words, target_words = target_words)
            # formatting text
            line_len = 0
            source_line = ''
            target_line = ''
            decode_text = ''
            for source_word, target_word in zip(source_words, target_words):
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
                    decode_text = f'{decode_text}{source_line}{target_line}{self.new_line}'
                    # set length to word length
                    line_len = word_len
                    # adjust word for same length, add word_space and add it to the line
                    source_line = source_word.ljust(word_len, ' ')
                    target_line = target_word.ljust(word_len, ' ')
                # if a punctuation mark is at the end of the word (end of sentence)
                elif any(punctuation in source_word for punctuation in self.regex.puncts):
                    # add word to the line and add self.new_line at the end
                    source_line = f'{source_line}{source_word}{self.new_line}'
                    target_line = f'{target_line}{target_word}{self.new_line}'
                    # combine to formatted text
                    decode_text = f'{decode_text}{source_line}{target_line}{self.new_line}'
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
            decode_text = f'{decode_text}{source_line}{target_line}{self.new_line}'

            self._save_decode_text(decode_text = decode_text)
            if translate:
                translated_text = self._translate_text(source_text = source_text)
                self._save_translated_text(translated_text = translated_text)
        except Exception:
            message = f'Could not decode source text to file with exception:\n{traceback.format_exc()}'
            logger.error(message)
            return

    def _save_decode_text(self, decode_text: str) -> str:
        destin_path, _ = self._get_destin_paths(source_path = self.source_path)
        if not os.path.isfile(destin_path) and decode_text:
            with open(file = destin_path, mode = 'w', encoding = 'utf-8') as file:
                file.write(decode_text)
            return destin_path

    def _translate_text(self, source_text) -> str:
        translated_text = self.translate_source(source_text)
        return textwrap.fill(translated_text, width = self.char_lim)

    def _save_translated_text(self, translated_text) -> str:
        _, transl_path = self._get_destin_paths(source_path = self.source_path)
        if not os.path.isfile(transl_path) and translated_text:
            with open(file = transl_path, mode = 'w', encoding = 'utf-8') as file:
                file.write(translated_text)
            return transl_path
