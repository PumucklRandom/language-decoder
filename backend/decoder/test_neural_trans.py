import os
from pprint import PrettyPrinter
from backend.decoder.neural_translator import NeuralTranslator

pp = PrettyPrinter(indent = 4)

# LanguageDecoder
URL = 'https://openrouter.ai/api/v1'
API_KEY = 'c2stb3ItdjEtMjFjZDU1NTg2M2I0ZWU4Mzg0MTI4MmEwNzA4ZTk2OGFjY2RmNmQyYmEzNzRlZGJhYmQyNzUxNjRmNWMyYzI3Mw=='
# the only usable model at the moment if not rate limited!
# MODEL_NAME = 'Google: Gemini 2.0 Flash Experimental'
MODEL_NAME = 'Google: Gemma 3 27B'
base_path = r'./'
prompt_path = os.path.join(base_path, 'prompt.txt')
source_path = os.path.join(base_path, 'source.txt')

with open(source_path, 'r', encoding = 'utf-8') as file:
    source_words = file.read().split()

translator = NeuralTranslator(
    source_language = 'russian',
    target_language = 'german',
    model_name = MODEL_NAME,
    model_temp = 0.0,
    model_seed = 0,
    api_url = URL,
    api_key = API_KEY
)
translator.prompt = translator._load_prompt(prompt_path = prompt_path)

# system: define task and rules
# user: provide the text e.g. CSV input for the translation process
# assistant: offer a sample translation or expected output format

target_words = translator.translate_batch(source_words = source_words)

# print(f'Translate words with: {MODEL_NAME}')
# response = translator.client.chat.completions.create(
#     messages = [  # system, user, assistant
#         {'role': 'system', 'content': translator._get_prompt()},
#         {'role': 'user', 'content': translator._to_csv(source_words)},
#         # {'role': 'assistant', 'content': 'Source\tTarget\n'}
#     ],
#     model = translator.models.get(MODEL_NAME),
#     temperature = 0.0,
#     seed = 0,
# )
# target_words = translator._check_content(
#     content = response.choices[0].message.content,
#     csv_len = len(source_words) + 1
# )

pp.pprint(list(zip(source_words, target_words)))
