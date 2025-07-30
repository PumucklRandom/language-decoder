import re
import json
from uuid import UUID
from typing import Union
from requests.exceptions import ConnectionError as HTTPConnectionError, ProxyError
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

    __slots__ = (
        'user_uuid',
        'source_language',
        'target_language',
        'source_text',
        'source_words',
        'target_words',
        'sentences',
        'dicts',
        'settings',
        '_normal_trans',
        '_neural_trans',
        'pattern'
    )

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
        self.source_text: str = ''
        self.source_words: list[str] = []
        self.target_words: list[str] = []
        self.sentences: list[str] = []
        self.dicts = Dicts(user_uuid = self.user_uuid)
        self.settings = Settings(user_uuid = self.user_uuid)
        self._normal_trans = NormalTranslator()
        self._neural_trans = NeuralTranslator()
        # creates two groups, that matches anything inside the \s
        self.pattern = re.compile(r'\[\s*(\S[\S ]*\S)\s*(\S[\S ]*\S)\s*\]')

    def _set_normal_trans(self) -> None:
        self._normal_trans.__config__(
            source_language = self.source_language,
            target_language = self.target_language,
            proxies = self.settings.get_proxies(),
            endofs = self.regex.endofs,
            quotes = self.regex.quotes
        )

    def _set_neural_trans(self) -> None:
        self._neural_trans.__config__(
            source_language = self.source_language,
            target_language = self.target_language,
            proxies = self.settings.get_proxies(),
            endofs = self.regex.endofs,
            quotes = self.regex.quotes,
            model_name = self.model_name,
        )

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
        except HTTPConnectionError:
            raise HTTPConnectionError
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
        if self.regex.quotes and self.regex.close and self.regex.endofs:
            # swap quotes/brackets with EndOfSentence marks if quotes/brackets are followed by EndOfSentence marks
            text = re.sub(rf'([{self.regex.quotes}{self.regex.close}])\s*([{self.regex.endofs}])', r'\2\1', text)
        if self.regex.begins and self.regex.opens:
            # remove any white whitespaces after "begin marks" and add one whitespace before "begin marks"
            text = re.sub(rf'([{self.regex.begins}{self.regex.opens}])\s*', r' \1', text)
        if self.regex.ending and self.regex.close:
            # remove any white whitespaces before "ending marks" and add one whitespace after "ending marks"
            text = re.sub(rf'\s*([{self.regex.ending}{self.regex.close}])', r'\1 ', text)
        if self.regex.digits:
            # remove any whitespaces around "digit marks"
            text = re.sub(rf'(\d)\s*([{self.regex.digits}])\s*(\d)', r'\1\2\3', text)
        if self.regex.puncts:
            # remove any white whitespaces before "punctuations" and add one whitespace after "punctuations"
            #   if "punctuations" are followed by letters or whitespace
            text = re.sub(rf'\s*([{self.regex.puncts}]+)([^\W\d_]|[{self.regex.puncts}\s])', r'\1 \2', text)
        for quote in self.regex.quotes:
            # remove any whitespaces inside quote pairs and add one whitespaces outside of quote pairs
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
    def split_text(self) -> None:
        if len(self.source_text) == 0:
            message = 'Source Text is empty'
            logger.error(message)
            raise DecoderError(message)
        # reformat text for translator
        if self.settings.app.reformatting:
            source_text = self._reformat_text(text = self.source_text)
        else:
            source_text = ' '.join(self.source_text.split())
        # split text into words
        self.source_words = source_text.split()

    @catch(DecoderError)
    def decode_words(self) -> None:
        logger.info(f'Decode {len(self.source_words)} words.')
        # strip source words before translation
        # source_words_strip = list(map(self._strip_word, source_words))
        target_words = self.translate(source = self.source_words)
        if len(target_words) != len(self.source_words):
            message = (f'Length mismatch between source words ({len(self.source_words)}) '
                       f'and target words ({len(target_words)})!')
            logger.error(message)
            raise DecoderError(message)
        self.target_words.clear()
        for source_word, target_word in zip(self.source_words, target_words):
            # take source word if target word is empty
            target_word = source_word if not target_word else target_word
            # add missing marks from source word to target word
            self.target_words.append(self._wrap_word(source_word = source_word, target_word = target_word))

    def _split_sentences(self, text: str) -> list[str]:
        # spit text into sentences with consideration of quotes and brackets
        return re.findall(rf'(.*?[{self.regex.endofs}][{self.regex.quotes}]?)\s+', f'{text} ')

    @catch(DecoderError)
    def translate_sentences(self) -> None:
        source_text = ' '.join(self.source_words)
        # add a dot at the end of the text in case of missing EndOfSentence mark
        if not any(mark in source_text.split()[-1] for mark in self.regex.endofs):
            source_text += '.'
        scr_sentences = self._split_sentences(text = source_text)
        logger.info(f'Decode {len(scr_sentences)} sentences.')
        tar_sentences = self.translate(source = scr_sentences, neural = False)
        if len(tar_sentences) != len(scr_sentences):
            message = (f'Length mismatch between source sentences ({len(scr_sentences)})'
                       f'and target sentences ({len(tar_sentences)})!')
            logger.error(message)
            raise DecoderError(message)
        self.sentences.clear()
        for source, target in zip(scr_sentences, tar_sentences):
            self.sentences.extend([source, target, '/N'])
        self.sentences.pop(-1)  # remove last '/N'

    @catch(DecoderError)
    def apply_dict(self) -> None:
        if not self.dicts.dict_name: return None
        self.dicts.load()
        dictionary = self.dicts.dictionaries.get(self.dicts.dict_name, {})
        target_words = self.target_words.copy()
        self.target_words.clear()
        for source_word, target_word in zip(self.source_words, target_words):
            # first strip the source word for the dictionary keys
            source_strip = self._strip_word(source_word)
            if source_strip in dictionary.keys():
                # replace target word if stripped source word is key
                target_word = dictionary.get(source_strip)
            # add missing marks from source word to target word
            self.target_words.append(self._wrap_word(source_word = source_word, target_word = target_word))
        return None

    @catch(DecoderError)
    def find_replace(self, find: str, repl: str) -> None:
        for i, (source, target) in enumerate(zip(self.source_words, self.target_words)):
            self.source_words[i] = source.replace(find, repl)
            self.target_words[i] = target.replace(find, repl)

    @catch(DecoderError)
    def from_json_str(self, data: str) -> None:
        try:
            data = json.loads(data)
            words_lists = list(zip(*data.get('decoded', [])))
            if not words_lists: raise DecoderError('Invalid json file')
            if len(words_lists) != 2:
                raise DecoderError('Unequal number of source and target words')
            if any(not isinstance(word, str) for word in words_lists[0] + words_lists[1]):
                raise DecoderError('Found a non-string value in data')
            self.source_words = list(words_lists[0])
            self.target_words = list(words_lists[1])
            self.sentences.clear()
            if all(isinstance(sentence, str) for sentence in data.get('sentences', [])):
                self.sentences = data.get('sentences', [])
        except DecoderError as exception:
            raise exception

    @catch(DecoderError)
    def to_json_str(self) -> str:
        data = {
            'decoded': list(zip(self.source_words, self.target_words)),
            'sentences': self.sentences
        }
        return re.sub(
            self.pattern,
            r'[\1 \2]',
            json.dumps(data, ensure_ascii = False, indent = 4)
        )
