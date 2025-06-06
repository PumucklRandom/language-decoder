import re
import json
from uuid import UUID
from typing import Union
from requests.exceptions import ConnectionError, ProxyError
from backend.error.error import DecoderError, NormalTranslatorError, NeuralTranslatorError, catch
from backend.logger.logger import logger
from backend.config.config import CONFIG, Regex
from backend.decoder.normal_translator import NormalTranslator
from backend.decoder.neural_translator import NeuralTranslator
from backend.user_data.dictionaries import Dicts
from backend.user_data.settings import Settings


class LanguageDecoder(object):
    """
    The LanguageDecoder translates a given source language to a desired target language word by word (decoding).
    It uses NormalTranslator for common translations and NeuralTranslator for advanced translations.
    """

    def __init__(self,
                 user_uuid: Union[UUID, str] = '00000000-0000-0000-0000-000000000000',
                 source_language: str = 'auto',
                 target_language: str = 'english') -> None:
        """
        :param user_uuid: user uuid to identify correspondent user data
        :param source_language: the translation source language
        :param target_language: the translation target language
        """
        self.user_uuid = '00000000-0000-0000-0000-000000000000' if CONFIG.on_prem else user_uuid
        self.source_language = source_language
        self.target_language = target_language
        self.dicts = Dicts(user_uuid = self.user_uuid)
        self.settings = Settings(user_uuid = self.user_uuid)
        self._normal_trans = NormalTranslator()
        self._neural_trans = NeuralTranslator()

    def _set_normal_trans(self) -> None:
        self._normal_trans.__config__(
            source_language = self.source_language,
            target_language = self.target_language,
            proxies = self.proxies,
            endofs = self.regex.endofs + self.regex.quotes
        )

    def _set_neural_trans(self) -> None:
        self._neural_trans.__config__(
            source_language = self.source_language,
            target_language = self.target_language,
            proxies = self.proxies,
            endofs = self.regex.endofs + self.regex.quotes,
            model_name = self.model_name,
        )

    @property
    def proxies(self) -> dict:
        return self.settings.get_proxies()

    @property
    def regex(self) -> Regex:
        return self.settings.regex

    @property
    def model_name(self) -> str:
        return self.settings.app.model_name

    @property
    def models(self) -> list[str]:
        return ['Google Translator'] + list(self._neural_trans.models.keys())

    @catch(DecoderError)
    def get_supported_languages(self, show: bool = False) -> list[str]:
        return self._normal_trans.get_supported_languages(show = show)

    def translate(self, source: list[str], neural = True) -> list[str]:
        try:
            if neural and self.model_name != 'Google Translator':
                self._set_neural_trans()
                return self._neural_trans.translate_batch(source)
            self._set_normal_trans()
            return self._normal_trans.translate_batch(source)
        except ProxyError:
            raise ProxyError
        except ConnectionError:
            raise ConnectionError
        except NormalTranslatorError as exception:
            raise DecoderError(exception.message, code = exception.code)
        except NeuralTranslatorError as exception:
            raise DecoderError(exception.message, code = exception.code)

    def _reformat_text(self, text: str) -> str:
        self.dicts.load()
        # remove new lines. for regex add whitespace at the end of text
        text = ' '.join(text.split()) + ' '
        # replace special characters with common ones
        for chars in self.settings.replacements.keys():
            text = text.replace(chars, self.settings.replacements.get(chars))
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

    @catch(DecoderError)
    def split_text(self, source_text: str) -> list[str]:
        if len(source_text) == 0:
            message = 'Source Text is empty'
            logger.error(message)
            raise DecoderError(message)
        # reformat text for translator
        if self.settings.app.reformatting:
            source_text = self._reformat_text(text = source_text)
        else:
            source_text = ' '.join(source_text.split())
        # split text into words
        return source_text.split()

    @catch(DecoderError)
    def decode_words(self, source_words: list[str]) -> list[str]:
        logger.info(f'Decode {len(source_words)} words.')
        # strip source words before translation
        # source_words_strip = list(map(self._strip_word, source_words))
        _target_words = self.translate(source = source_words)
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

    def _split_sentences(self, text: str) -> list[str]:
        # spit text into sentences with consideration of quotes and brackets
        return re.findall(rf'(.*?[{self.regex.endofs}][{self.regex.quotes}]?)\s+', f'{text} ')

    @catch(DecoderError)
    def translate_sentences(self, source_words: list[str]) -> list[str]:
        text = ' '.join(source_words)
        # add a dot at the end of the text in case of missing EndOfSentence mark
        if not any(mark in text.split()[-1] for mark in self.regex.endofs):
            text += '.'
        scr_sentences = self._split_sentences(text = text)
        logger.info(f'Decode {len(scr_sentences)} sentences.')
        tar_sentences = self.translate(source = scr_sentences, neural = False)
        if len(tar_sentences) != len(scr_sentences):
            message = 'Length mismatch between source and target sentences'
            logger.error(message)
            raise DecoderError(message)
        sentences = list()
        for source, target in zip(scr_sentences, tar_sentences):
            sentences.extend([source, target, '/N'])
        sentences.pop(-1)
        return sentences

    @catch(DecoderError)
    def apply_dict(self, source_words: list[str], target_words: list[str]) -> list[str]:
        if not self.dicts.dict_name: return target_words
        self.dicts.load()
        dictionary = self.dicts.dictionaries.get(self.dicts.dict_name, {})
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

    @staticmethod
    @catch(DecoderError)
    def find_replace(source_words: list[str], target_words: list[str],
                     find: str, repl: str) -> tuple[list[str], list[str]]:
        for i, (source, target) in enumerate(zip(source_words, target_words)):
            source_words[i] = source.replace(find, repl)
            target_words[i] = target.replace(find, repl)
        return source_words, target_words

    @staticmethod
    @catch(DecoderError)
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

    @staticmethod
    @catch(DecoderError)
    def to_json_str(source_words: list[str], target_words: list[str], sentences: list[str]) -> str:
        data = {'decoded': list(zip(source_words, target_words)), 'sentences': sentences}
        return re.sub(r'\[\s*"([^"]*)",\s*"([^"]*)"\s*\]', r'["\1", "\2"]',
                      json.dumps(data, ensure_ascii = False, indent = 4))
