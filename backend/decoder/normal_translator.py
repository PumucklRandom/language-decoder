import traceback
from typing import Optional
from pprint import PrettyPrinter
from requests.exceptions import ConnectionError, ProxyError
from deep_translator.exceptions import BaseError, RequestError, TooManyRequests
from deep_translator import GoogleTranslator
from backend.error.error import NormalTranslatorError
from backend.logger.logger import logger
from backend.config.config import CONFIG
from backend.utils import utilities as utils


class NormalTranslator(object):
    """
    NormalTranslator is used to provide a simple interface for normal translators like GoogleTranslator.
    """

    def __init__(self,
                 source_language: str = 'auto',
                 target_language: str = 'english',
                 proxies: Optional[dict] = None,
                 endofs: str = '.!?\'"',
                 **kwargs) -> None:
        """
        :param source_language: the translation source language
        :param target_language: the translation target language
        :param proxies: set proxies for translator
        :param endofs: end of sentence characters to split sentences
        """
        self._translator = GoogleTranslator(
            source = source_language,
            target = target_language,
            proxies = proxies,
            **kwargs
        )
        self.endofs = endofs

    def __config__(self, source_language: str, target_language: str,
                   proxies: Optional[dict] = None, endofs: str = '.!?\'"') -> None:
        self._translator.source, self._translator.target = self._translator._map_language_to_code(  # noqa
            source_language, target_language)
        self._translator.proxies = proxies
        self.endofs = endofs

    def get_supported_languages(self, show: bool = False) -> list[str]:
        languages = self._translator.get_supported_languages(as_dict = True)
        if show: PrettyPrinter(indent = 4).pprint(languages.keys())
        return list(languages.keys())

    def translate_batch(self, source_words: list[str]) -> list[str]:
        result = list()
        for batch in utils.yield_batch_eos(source_words, char_limit = CONFIG.char_limit, endofs = self.endofs):
            result.extend(self._translate(batch))
        return result

    def _translate(self, source_words: list[str]) -> list[str]:
        try:
            return self._translator.translate('\n'.join(source_words)).split('\n')
        except ProxyError as exception:
            message = 'Proxy Error! Check your proxy settings!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise ProxyError
        except ConnectionError as exception:
            message = 'Connection Error! Check your internet connection!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise ConnectionError
        except TooManyRequests as exception:
            message = 'Too many requests! Try again later!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise NormalTranslatorError(message, code = 429)
        except RequestError as exception:
            message = 'Bad Request Error! Check your request and try again!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise NormalTranslatorError(message, code = 400)
        except BaseError as exception:
            message = 'Unexpected API Error!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise NormalTranslatorError(message, code = 500)
