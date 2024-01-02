import os
from glob import glob
from language_decoder.language_decoder import LanguageDecoder
from language_decoder.dictionaries import REPLACEMENTS, RU2DE

# Initialise language decoder.
language_decoder = LanguageDecoder(source_language = 'ru', target_language = 'de',
                                   replace_dict = REPLACEMENTS, dictionary = RU2DE)
base_path = 'C:/Users/User/source/'
directories = glob(os.path.join(base_path, '**/*/'), recursive = True)
for directory in directories:
    text_files = glob(os.path.join(directory, '*.txt'))
    for text_file in text_files:
        if not text_file.endswith('transl.txt') and not text_file.endswith('decode.txt'):
            language_decoder.decode_text(source_path = text_file, translate_text = True)
        if text_file.endswith('decode.txt'):
            language_decoder.convert2pdf(decode_path = text_file)
            # language_decoder.delete_decoded_files(decode_path=text_file)
