import os
from glob import glob
from backend.decoder.pdf import PDF
from backend.decoder.language_decoder import LanguageDecoder


def main():
    # Initialise language decoder.
    pdf = PDF()
    language_decoder = LanguageDecoder(source_language = 'ru', target_language = 'de', dict_name = 'RU2DE')

    base_path = 'C:/Users/User/source/'
    directories = glob(os.path.join(base_path, '**/*/'), recursive = True)
    for directory in directories:
        text_files = glob(os.path.join(directory, '*.txt'))
        for text_file in text_files:
            if not text_file.endswith('transl.txt') and not text_file.endswith('decode.txt'):
                language_decoder.decode_text_to_file(source_path = text_file, translate = True)
            if text_file.endswith('decode.txt'):
                pdf.convert2pdf(decode_path = text_file)
                # language_decoder.delete_decoded_files(decode_path=text_file)


main()
