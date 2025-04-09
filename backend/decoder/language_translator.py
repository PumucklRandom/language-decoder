import os
import io
import csv
import httpx
import base64
import traceback
import openai
from openai import OpenAI, OpenAIError
from typing import List
from backend.config.config import CONFIG
from backend.error.error import ConfigError
from backend.logger.logger import logger


class LanguageTranslator(object):
    """
    The LanguageTranslator uses NLP to literal translate source words to the desired target words.
    Therefor open and free available LLMs/GPTs are used to perform the translation.
    """

    def __init__(self,
                 source: str = 'auto',
                 target: str = 'english',
                 model: str = CONFIG.model,
                 model_temp: float = CONFIG.model_temp,
                 model_seed: int = CONFIG.model_seed,
                 proxies: dict = None) -> None:

        """
        :param source: the translation source language
        :param target: the translation target language
        :param model: LLM/GPT model type
        :param model_temp: model temperature to adapt model 'creativity' and 'determinism'
        :param model_seed: model seed to adapt 'determinism'
        :param proxies: set proxies for translator
        """

        self.source = source
        self.target = target
        self.model = model
        self.model_temp = model_temp
        self.model_seed = model_seed
        self.prompt = self.load_prompt()
        self.client = OpenAI(
            base_url = CONFIG.api_url,
            api_key = self.decode_key(CONFIG.api_key),
        )
        self.set_proxy(proxies = proxies)

    def __config__(self, source: str, target: str, proxies: dict = None) -> None:
        self.source = source
        self.target = target
        self.set_proxy(proxies = proxies)

    def set_proxy(self, proxies: dict = None) -> None:
        if isinstance(proxies, dict):
            if proxies.get('http', None):
                proxies.update({'http://': httpx.HTTPTransport(proxy = f'http://{proxies.get("http")}')})
            if proxies.get('https', None):
                proxies.update({'https://': httpx.HTTPTransport(proxy = f'http://{proxies.get("https")}')})
            proxies.pop('http', None)
            proxies.pop('https', None)
        self.client._client = httpx.Client(mounts = proxies)

    def translate(self, source_words: List[str]) -> List[str]:
        try:
            csv_string = self.to_csv(source_words)
            response = self.client.chat.completions.create(
                messages = [
                    {'role': 'system', 'content': self.get_prompt()},
                    {'role': 'user', 'content': csv_string},
                    # {'role': 'assistant', 'content': 'Source\tTarget\n'}
                ],
                model = self.model,
                temperature = self.model_temp,
                seed = self.model_seed,
            )
            return self.check_response(
                content = response.choices[0].message.content,
                csv_len = len(csv_string.split('\n')) - 1  # -1 because of last \n
            )
        except openai.RateLimitError:
            message = 'Rate Limit is reached! Try again on another day!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise OpenAIError(message)
        except openai.BadRequestError:
            message = 'Bad Request Error! Check your request and try again!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise OpenAIError(message)
        except openai.APIConnectionError:
            message = 'Connection Error! Check your internet connection or your proxy settings!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise OpenAIError(message)
        except openai.AuthenticationError:
            message = 'Authentication Error! Check your API key and your permissions!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise OpenAIError(message)
        except Exception:
            message = 'Unexpected Error!'
            logger.error(f'{message} with exception:\n{traceback.format_exc()}')
            raise Exception(message)

    def check_response(self, content: str, csv_len: int) -> List[str]:
        rows = content.split('\n')
        invalid_rows = list()
        for row in rows:
            if '\t' not in row:
                invalid_rows.append(row)
        # remove rows without "\t"
        for row in invalid_rows: rows.remove(row)
        # ensure, that the list is as long as the input
        rows = rows + [rows[-1]] * (csv_len - len(rows))
        # ensure, that the list is max length of the input
        return self.from_csv('\n'.join(rows[:csv_len]))

    def get_prompt(self) -> str:
        return self.prompt.replace('<SOURCE>', f'{self.source}').replace('<TARGET>', f'{self.target}')

    @staticmethod
    def encode_key(api_key: str) -> str:
        return base64.b64encode(api_key.encode()).decode()

    @staticmethod
    def decode_key(api_key: str) -> str:
        return base64.b64decode(api_key.encode()).decode()

    @staticmethod
    def to_csv(source_words: List[str]) -> str:
        with io.StringIO() as io_string:
            csv_writer = csv.writer(io_string, delimiter = '\t', lineterminator = '\n')
            csv_writer.writerows([('Source', 'Target')] + list(zip(source_words)))
            return io_string.getvalue()

    @staticmethod
    def from_csv(csv_string: str) -> List[str]:
        with io.StringIO(csv_string) as io_string:
            return list(list(zip(*list(csv.reader(io_string, delimiter = '\t'))[1:]))[-1])

    @staticmethod
    def load_prompt(prompt_path: str = 'prompt.txt') -> str:
        prompt_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), prompt_path)
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
