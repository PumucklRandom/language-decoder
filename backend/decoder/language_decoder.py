import os
import re
import json
import requests
import traceback
from uuid import UUID
from openai import OpenAIError
from pprint import PrettyPrinter
from typing import Tuple, List, Union
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError, TooManyRequests, TranslationNotFound
from backend.decoder.language_translator import LanguageTranslator
from backend.config.config import CONFIG, Config
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.dicts.dictonaries import Dicts
from backend.utils import utilities as utils


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
                 char_limit: int = CONFIG.char_limit,
                 proxies: dict = None,
                 regex: Config.Regex = CONFIG.Regex) -> None:

        """
        :param user_uuid: user uuid to identify correspondent dictionaries
        :param source_language: the translation source language
        :param target_language: the translation target language
        :param dict_name: the name of the dictionary to select the desires dictionary
        :param new_line: new line string
        :param char_limit: character limit of one translation batch
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
        self.regex = regex
        self.new_line = new_line
        self.char_limit = char_limit
        self.source_path: str = ''
        self.reformatting: bool = True
        self.alt_trans: bool = False
        self._translator = GoogleTranslator(
            source = self.source_language,
            target = self.target_language,
            proxies = self.proxies
        )
        self._langslator = LanguageTranslator(
            source = self.source_language,
            target = self.target_language,
            proxies = self.proxies
        )

    def config_translator(self):
        self._translator.source, self._translator.target = self._translator._map_language_to_code(  # noqa
            self.source_language, self.target_language)
        self._translator.proxies = self.proxies

    def config_langslator(self):
        self._langslator.__config__(
            source = self.source_language,
            target = self.target_language,
            proxies = self.proxies
        )

    def get_supported_languages(self, show: bool = False) -> List[str]:
        try:
            languages = self._translator.get_supported_languages(as_dict = True)
            if show: self._pp.pprint(languages.keys())
            return list(languages.keys())
        except Exception:
            message = f'Could not fetch supported languages with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    def translate_batch(self, source: List[str]) -> List[str]:
        result = list()
        for batch in utils.yield_batch(source, self.char_limit):
            result.extend(self._translator.translate('\n'.join(batch)).split('\n'))
        return result

    def translate(self, source: Union[List[str], str], alt_trans: bool = False) -> Union[List[str], str]:
        try:
            if isinstance(source, list):
                if self.alt_trans and alt_trans:
                    self.config_langslator()
                    return self._langslator.translate(source)
                self.config_translator()
                return self.translate_batch(source)
            self.config_translator()
            return self._translator.translate(source)
        except TooManyRequests:
            message = 'Too many requests! Try again later!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise DecoderError(message)
        except RequestError:
            message = 'Bad Request Error! Check your request and try again!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise DecoderError(message)
        except requests.exceptions.ProxyError:
            message = 'Connection Error! Check your internet connection or your proxy settings!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise DecoderError(message)
        except TranslationNotFound:
            message = 'Translator Error!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise DecoderError(message)
        except OpenAIError:
            message = 'OpenAI Error!'
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
            # text = self._split_camel_case(text)
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
            target_words_strip = self.translate(source = source_words_strip, alt_trans = True)
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
            return target_words
        except Exception:
            message = f'Could not decode source words with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    def _split_sentences(self, text: str) -> List[str]:
        # spit text into sentences with consideration of quotes and brackets
        return re.findall(f'(.*?[{self.regex.puncts}][{self.regex.close}{self.regex.quotes}]?)\s+', f'{text} ')

    def decode_sentences(self, source_words: List[str]) -> List[str]:

        text = ' '.join(source_words)
        if not any(punctuation in text.split()[-1] for punctuation in self.regex.puncts):
            text += '.'
        scr_sentences = self._split_sentences(text = text)
        logger.info(f'Decode {len(scr_sentences)} sentences.')
        tar_sentences = self.translate(source = scr_sentences)
        if len(tar_sentences) != len(scr_sentences):
            message = 'Length mismatch between source and target sentences'
            logger.error(message)
            raise DecoderError(message)
        sentences = list()
        for source, target in zip(scr_sentences, tar_sentences):
            sentences.extend([source, target, '/N'])
        sentences.pop(-1)
        return sentences

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
    def find_replace(source_words: List[str], target_words: List[str],
                     find: str, repl: str) -> Tuple[List[str], List[str]]:
        for i, (source, target) in enumerate(zip(source_words, target_words)):
            source_words[i] = source.replace(find, repl)
            target_words[i] = target.replace(find, repl)
        return source_words, target_words

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
