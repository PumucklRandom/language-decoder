import os
from pprint import PrettyPrinter
from backend.decoder.language_translator import LanguageTranslator

pp = PrettyPrinter(indent = 4)

# LanguageDecoder
URL = 'https://openrouter.ai/api/v1'
API_KEY = 'c2stb3ItdjEtMjFjZDU1NTg2M2I0ZWU4Mzg0MTI4MmEwNzA4ZTk2OGFjY2RmNmQyYmEzNzRlZGJhYmQyNzUxNjRmNWMyYzI3Mw=='
MODEL = 'google/gemini-2.0-flash-exp:free'
# MODEL = 'google/learnlm-1.5-pro-experimental:free'
# MODEL = 'deepseek/deepseek-chat:free'

base_path = r'./'
prompt_path = os.path.join(base_path, 'prompt.txt')
source_path = os.path.join(base_path, 'source.txt')

with open(source_path, 'r', encoding = 'utf-8') as file:
    source = file.read()
    source_words = source.split()

langslator = LanguageTranslator(
    api_url = URL,
    api_key = API_KEY,
    model = MODEL,
    model_temp = 0.0,
    model_seed = 0,
    source = 'russian',
    target = 'german',
)
langslator.prompt = langslator.load_prompt(prompt_path = prompt_path)

# system: define task and rules
# user: provide the text e.g. CSV input for the translation process
# assistant: offer a sample translation or expected output format

target_words = langslator.translate(source_words = source_words)

# response = langslator.client.chat.completions.create(
#     messages = [  # system, user, assistant
#         {'role': 'system', 'content': langslator.get_prompt()},
#         {'role': 'user', 'content': langslator.to_csv(source_words)},
#         # {'role': 'assistant', 'content': 'Source\tTarget\n'}
#     ],
#     model = MODEL,
#     temperature = 0.0,
#     seed = 0,
# )
# target_words = langslator.check_content(
#     content = response.choices[0].message.content,
#     csv_len = len(source_words) + 1
# )

pp.pprint(list(zip(source_words, target_words)))
