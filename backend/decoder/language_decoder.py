import re
import json
import requests
import traceback
from uuid import UUID
from openai import OpenAIError
from pprint import PrettyPrinter
from typing import Union
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError, TooManyRequests, TranslationNotFound
from backend.decoder.language_translator import LanguageTranslator
from backend.config.config import CONFIG, Config
from backend.error.error import DecoderError
from backend.logger.logger import logger
from backend.dicts.dictionaries import Dicts
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
                 new_line: str = '\n',
                 char_limit: int = CONFIG.char_limit,
                 proxies: dict = None,
                 regex: Config.Regex = CONFIG.Regex) -> None:

        """
        :param user_uuid: user uuid to identify correspondent dictionaries
        :param source_language: the translation source language
        :param target_language: the translation target language
        :param new_line: new line string
        :param char_limit: character limit of one translation batch
        :param proxies: set proxies for translator
        :param regex: a set of character patterns for regex compilations
        """

        self._pp = PrettyPrinter(indent = 4)
        self.user_uuid = user_uuid
        self.source_language = source_language
        self.target_language = target_language
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

    def config_translator(self) -> None:
        self._translator.source, self._translator.target = self._translator._map_language_to_code(  # noqa
            self.source_language, self.target_language)
        self._translator.proxies = self.proxies

    def config_langslator(self) -> None:
        self._langslator.__config__(
            source = self.source_language,
            target = self.target_language,
            proxies = self.proxies
        )

    def get_supported_languages(self, show: bool = False) -> list[str]:
        try:
            languages = self._translator.get_supported_languages(as_dict = True)
            if show: self._pp.pprint(languages.keys())
            return list(languages.keys())
        except Exception:
            message = f'Could not fetch supported languages with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    def translate_batch(self, source: list[str]) -> list[str]:
        result = list()
        for batch in utils.yield_batch_eos(source, self.char_limit, endofs = self.regex.endofs + self.regex.quotes):
            result.extend(self._translator.translate('\n'.join(batch)).split('\n'))
        return result

    def translate(self, source: Union[list[str], str], alt_trans: bool = False) -> Union[list[str], str]:
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

    def _reformat_text(self, text: str) -> str:
        try:
            # remove new lines. for regex add whitespace at the end of text
            text = ' '.join(text.split()) + ' '
            self._dicts.load(user_uuid = self.user_uuid)
            # replace special characters with common ones
            for chars in self._dicts.replacements.keys():
                text = text.replace(chars, self._dicts.replacements.get(chars))
            # swap quotes/brackets with EndOfSentence marks if quotes/brackets are followed by EndOfSentence marks
            text = re.sub(rf'([{self.regex.quotes}{self.regex.close}])\s*([{self.regex.endofs}])', r'\2\1', text)
            # remove any white whitespaces after "begin marks" and add one whitespace before "begin marks"
            text = re.sub(rf'([{self.regex.begins}{self.regex.opens}])\s*', r' \1', text)
            # remove any white whitespaces before "ending marks" and add one whitespace after "ending marks"
            text = re.sub(rf'\s*([{self.regex.ending}{self.regex.close}])', r'\1 ', text)
            # remove any whitespaces around "digit marks"
            text = re.sub(rf'(\d)\s*([{self.regex.digits}])\s*(\d)', r'\1\2\3', text)
            # remove any white whitespaces before "punctuations" and add one whitespace after "punctuations"
            #   if "punctuations" are followed by letters or whitespace
            text = re.sub(rf'\s*([{self.regex.puncts}]+)([^\W\d_]|[{self.regex.puncts}\s])', r'\1 \2', text)
            # remove any whitespaces inside quote pairs and add one whitespaces outside of quote pairs
            for quote in self.regex.quotes:
                text = re.sub(rf'([{quote}])\s*(.*?)\s*([{quote}])', r' \1\2\3 ', text)
            # remove redundant whitespaces
            text = ' '.join(text.split())
            # add a dot at the end of the text in case of missing EndOfSentence mark
            if not any(mark in text.split()[-1] for mark in self.regex.endofs):
                text += '.'
            return text
        except Exception:
            message = f'Could not reformat source text with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    @staticmethod
    def _strip_word(word: str) -> str:
        # check word if all non-alphanumeric
        if bool(re.fullmatch(r'[\W_]*', word)):
            return word
        # remove all non-alphanumeric and non-minus characters
        return re.sub(r'\A[\W_]*|[\W_]*\Z', '', word)

    def _wrap_word(self, source_word: str, target_word: str) -> str:
        # make sure target word is stripped
        target_word = self._strip_word(target_word)
        # check source word if all non-alphanumeric
        if bool(re.fullmatch(r'[\W_]*', source_word)):
            return source_word
        # get marks at the beginning of the source word
        beg = re.search(r'\A[\W_]*', source_word).group()
        # get marks at the end of the source word
        end = re.search(r'[\W_]*\Z', source_word).group()
        # add marks around the target word
        return f'{beg}{target_word}{end}'

    def split_text(self, source_text: str) -> list[str]:
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

    def decode_words(self, source_words: list[str]) -> list[str]:
        try:
            logger.info(f'Decode {len(source_words)} words.')
            # strip source words before translation
            # source_words_strip = list(map(self._strip_word, source_words))
            _target_words = self.translate(source = source_words, alt_trans = True)
            if len(_target_words) != len(source_words):
                message = (f'Length mismatch between source words ({len(source_words)}) '
                           f'and target words ({len(_target_words)})')
                logger.error(message)
                raise DecoderError(message)
            target_words = list()
            for source_word, target_word in zip(source_words, _target_words):
                # take source word if target word is empty
                target_word = source_word if not target_word else target_word
                # add missing marks from source word to target word
                target_words.append(self._wrap_word(source_word = source_word, target_word = target_word))
            return target_words
        except Exception:
            message = f'Could not decode source words with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    def _split_sentences(self, text: str) -> list[str]:
        # spit text into sentences with consideration of quotes and brackets
        return re.findall(rf'(.*?[{self.regex.endofs}][{self.regex.quotes}]?)\s+', f'{text} ')

    def translate_sentences(self, source_words: list[str]) -> list[str]:
        try:
            text = ' '.join(source_words)
            # add a dot at the end of the text in case of missing EndOfSentence mark
            if not any(mark in text.split()[-1] for mark in self.regex.endofs):
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
        except Exception:
            message = f'Could not translate sentences with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)

    def apply_dict(self, source_words: list[str], target_words: list[str], dict_name: str = '') -> list[str]:
        try:
            if not dict_name: return target_words
            self._dicts.load(user_uuid = self.user_uuid)
            dictionary = self._dicts.dictionaries.get(dict_name, {})
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
    def find_replace(source_words: list[str], target_words: list[str],
                     find: str, repl: str) -> tuple[list[str], list[str]]:
        for i, (source, target) in enumerate(zip(source_words, target_words)):
            source_words[i] = source.replace(find, repl)
            target_words[i] = target.replace(find, repl)
        return source_words, target_words

    @staticmethod
    def from_json_str(data: str) -> tuple[list[str], list[str], list[str]]:
        try:
            data = json.loads(data)
            words_lists = list(zip(*data.get('decoded', [])))
            if not words_lists: raise DecoderError('Invalid json file')
            if len(words_lists) != 2:
                raise DecoderError('Unequal number of source and target words')
            if any(not isinstance(word, str) for word in words_lists[0] + words_lists[1]):
                raise DecoderError('Found a non-string value in data')
            source_words = list(words_lists[0])
            target_words = list(words_lists[1])
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
    def to_json_str(source_words: list[str], target_words: list[str], sentences: list[str]) -> str:
        try:
            data = {'decoded': list(zip(source_words, target_words)), 'sentences': sentences}
            return re.sub(r'\[\s*"([^"]*)",\s*"([^"]*)"\s*\]', r'["\1", "\2"]',
                          json.dumps(data, ensure_ascii = False, indent = 4))
        except Exception:
            message = f'Could not execute export with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise DecoderError(message)
