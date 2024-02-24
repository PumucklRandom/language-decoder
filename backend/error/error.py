class LanguageDecoderError(Exception):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class BackendError(LanguageDecoderError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class FrontendError(LanguageDecoderError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class ConfigError(BackendError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class DictionaryError(BackendError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class DecoderError(BackendError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class PDFFormatterError(BackendError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class UIPageError(FrontendError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class StartPageError(UIPageError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class UploadPageError(UIPageError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class DecodingPageError(UIPageError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class DictionaryPageError(UIPageError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message


class SettingsPageError(UIPageError):
    def __init__(self, message: str = ''):
        super().__init__(message)
        self.message = message
