class LanguageDecoderError(Exception):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message, code)
        self.message = message
        self.code = code


class BackendError(LanguageDecoderError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class FrontendError(LanguageDecoderError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class ConfigError(BackendError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class DictionaryError(BackendError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class DecoderError(BackendError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class PDFFormatterError(BackendError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class UIPageError(FrontendError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class StartPageError(UIPageError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class UploadPageError(UIPageError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class DecodingPageError(UIPageError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class DictionaryPageError(UIPageError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)


class SettingsPageError(UIPageError):
    def __init__(self, message: str = '', code: str = ''):
        super().__init__(message = message, code = code)
