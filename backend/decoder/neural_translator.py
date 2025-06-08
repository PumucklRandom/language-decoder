import os
import io
import csv
import time
import httpx
import base64
import openai
import traceback
from requests.exceptions import ConnectionError as HTTPConnectionError, ProxyError
from openai import APIStatusError, BadRequestError, RateLimitError
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from backend.error.error import ConfigError, NeuralTranslatorError
from backend.logger.logger import logger
from backend.config.config import CONFIG
from backend.utils import utilities as utils

file_dir = os.path.dirname(os.path.relpath(__file__))


class NeuralTranslator(object):
    """
    The NeuralTranslator uses NLP to literal translate source words to the desired target words.
    For that open and free available LLMs/GPTs are used to perform the translation.
    """
    PROMPT: str = ''

    def __init__(self,
                 source_language: str = 'auto',
                 target_language: str = 'english',
                 proxies: dict = None,
                 endofs: str = '.!?\'"',
                 model_name: str = CONFIG.model_name,
                 model_temp: float = CONFIG.model_temp,
                 model_seed: int = CONFIG.model_seed,
                 api_url: str = CONFIG.api_url,
                 api_key: str = CONFIG.api_key) -> None:
        """
        :param source_language: the translation source language
        :param target_language: the translation target language
        :param proxies: set proxies for translator
        :param endofs: end of sentence characters to split sentences
        :param model_name: LLM/GPT model name
        :param model_temp: model temperature to adapt model 'creativity' and 'determinism'
        :param model_seed: model seed to adapt 'determinism'
        :param api_url: api url to model site
        :param api_key: api key to get access
        """
        self.source_language = source_language
        self.target_language = target_language
        self.model_name = model_name
        self.model_temp = model_temp
        self.model_seed = model_seed
        self.endofs = endofs
        if not NeuralTranslator.PROMPT:
            NeuralTranslator.PROMPT = self._load_prompt()
        self.client = openai.OpenAI(
            base_url = api_url,
            api_key = self._decode_key(api_key),
        )
        self._set_proxy(proxies = proxies)
        self.models = self.get_available_models()

    def __config__(self, source_language: str, target_language: str, model_name: str,
                   proxies: dict = None, endofs: str = '.!?\'"') -> None:
        self.source_language = source_language
        self.target_language = target_language
        if self.model_name in self.models.keys():
            self.model_name = model_name
        else:
            self.model_name = CONFIG.model_name
        self._set_proxy(proxies = proxies)
        self.endofs = endofs

    def _set_proxy(self, proxies: dict = None) -> None:
        if isinstance(proxies, dict):
            if proxies.get('http', ''):
                proxies.update({'http://': httpx.HTTPTransport(proxy = f'http://{proxies.get("http")}')})
            if proxies.get('https', ''):
                proxies.update({'https://': httpx.HTTPTransport(proxy = f'http://{proxies.get("https")}')})
            proxies.pop('http', None)
            proxies.pop('https', None)
        self.client._client = httpx.Client(mounts = proxies)

    def get_available_models(self) -> dict[str, str]:
        time_date = time.time() - CONFIG.model_age * 2592000  # 30d * 24h * 3600s per months
        models = tuple(
            model for model in self.client.models.list().data if ':free' in model.id
            and model.context_length >= CONFIG.model_context and model.created >= time_date
            and model.architecture.get('modality') in ('text->text', 'text+image->text')
            and {'temperature'}.issubset(model.supported_parameters)
            and {'reasoning', 'include_reasoning'}.isdisjoint(model.supported_parameters)
        )
        return {model.name.removesuffix(' (free)'): model.id for model in models}

    def translate_batch(self, source_words: list[str]) -> list[str]:
        result = list()
        for batch in utils.yield_batch_eos(source_words, char_limit = CONFIG.char_limit, endofs = self.endofs):
            result.extend(self._translate(batch))
        return result

    def _translate(self, source_words: list[str]) -> list[str]:
        try:
            logger.info(f'Translate words with: {self.model_name}')
            response = self.client.chat.completions.create(
                messages = [
                    ChatCompletionSystemMessageParam(role = 'system', content = self._get_prompt()),
                    ChatCompletionUserMessageParam(role = 'user', content = self._to_csv(source_words))
                    # ChatCompletionAssistantMessageParam(content = 'Source\tTarget\n')
                ],
                model = self.models.get(self.model_name),
                temperature = self.model_temp,
                # top_k = 10,
                # top_p = 0.5,
                # frequency_penalty = 0.0,  # + for frequent word penalty
                seed = self.model_seed,
                extra_headers = {
                    "X-Title": "LanguageDecoder",
                    # "HTTP-Referer": "LanguageDecoder",
                },
            )
            if not response.choices[0].message.content: return source_words

            return self._check_content(
                content = response.choices[0].message.content,
                csv_len = len(source_words) + 1
            )
        except ProxyError as exception:
            message = 'Proxy Error! Check your proxy settings!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise ProxyError
        except HTTPConnectionError as exception:
            message = 'Connection Error! Check your internet connection!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise HTTPConnectionError
        except RateLimitError as exception:
            message = 'Rate Limit is reached! Try again on another day!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise NeuralTranslatorError(message, code = exception.status_code)
        except BadRequestError as exception:
            message = 'Bad Request Error! Check your request and try again!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise NeuralTranslatorError(message, code = exception.status_code)
        except APIStatusError as exception:
            message = 'Unexpected API Error!'
            logger.error(f'{message} with exception: {exception}\n{traceback.format_exc()}')
            raise NeuralTranslatorError(message, code = exception.status_code)

    def _check_content(self, content: str, csv_len: int) -> list[str]:
        # get only valid rows
        valid_rows = [row for row in content.split('\n') if '\t' in row]
        # ensure, that the list is as long as the input
        valid_rows.extend([valid_rows[-1]] * (csv_len - len(valid_rows)))
        # ensure, that the list is max length of the input
        return self._from_csv('\n'.join(valid_rows[:csv_len]))

    def _get_prompt(self) -> str:
        return self.PROMPT.replace('<SOURCE>', self.source_language).replace('<TARGET>', self.target_language)

    @staticmethod
    def _encode_key(api_key: str) -> str:
        return base64.b64encode(api_key.encode()).decode()

    @staticmethod
    def _decode_key(api_key: str) -> str:
        return base64.b64decode(api_key.encode()).decode()

    @staticmethod
    def _to_csv(source_words: list[str]) -> str:
        with io.StringIO() as io_string:  # type: io.StringIO
            csv_writer = csv.writer(io_string, delimiter = '\t', lineterminator = '\n')
            csv_writer.writerows([('Source', 'Target')] + list(zip(source_words)))
            return io_string.getvalue()

    @staticmethod
    def _from_csv(csv_string: str) -> list[str]:
        with io.StringIO(csv_string) as io_string:
            return [row[-1] for row in csv.reader(io_string, delimiter = '\t')][1:]

    @classmethod
    def _load_prompt(cls, prompt_path: str = 'prompt.txt') -> str:
        prompt_path = os.path.join(file_dir, prompt_path)
        if not os.path.isfile(prompt_path):
            message = f'Prompt file not found at "{prompt_path}"'
            logger.critical(message)
            raise ConfigError(message)
        try:
            with open(file = prompt_path, mode = 'r', encoding = 'utf-8') as file:
                return file.read()
        except Exception:
            message = f'Could not parse prompt file with exception:\n{traceback.format_exc()}'
            logger.critical(message)
            raise ConfigError(message)
