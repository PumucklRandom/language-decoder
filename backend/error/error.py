import traceback
import functools
from typing import Type
from backend.logger.logger import logger


class LanguageDecoderError(Exception):
    __slots__ = ('message', 'code')

    def __init__(self, message: str = '', code: int = 500):
        super().__init__(message, code)
        self.message = message
        self.code = code


class BackendError(LanguageDecoderError):
    """Base exception class for backend errors."""
    __slots__ = ()


class ConfigError(BackendError):
    """Exception raised for configuration errors."""
    __slots__ = ()


class DecoderError(BackendError):
    """Exception raised for decoder-related errors."""
    __slots__ = ()


class PDFFormatterError(BackendError):
    """Exception raised for PDF formatter-related errors."""
    __slots__ = ()


class DictionaryError(BackendError):
    """Exception raised for dictionary-related errors."""
    __slots__ = ()


class SettingsError(BackendError):
    """Exception raised for settings-related errors."""
    __slots__ = ()


class NormalTranslatorError(DecoderError):
    """Exception raised for decoder-related errors."""
    __slots__ = ()


class NeuralTranslatorError(DecoderError):
    """Exception raised for decoder-related errors."""
    __slots__ = ()


class FrontendError(LanguageDecoderError):
    """Base exception class for frontend errors."""
    __slots__ = ()


class UIConfigError(FrontendError):
    """Exception raised for ui configuration errors."""
    __slots__ = ()


def catch(error: Type[LanguageDecoderError]) -> callable:
    def decorator(func: callable) -> callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> any:
            try:
                return func(*args, **kwargs)
            except Exception as exception:
                message = f'Error in "{func.__name__}" with exception: {exception}\n{traceback.format_exc()}'
                logger.error(message)
                code = exception.code if hasattr(exception, 'code') else 500
                raise error(message, code = code)

        return wrapper

    return decorator
