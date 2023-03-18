import os
import textwrap
from glob import glob
from fpdf import FPDF
from typing import Optional, Tuple, List
from pprint import PrettyPrinter
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError, TooManyRequests, MicrosoftAPIerror

pp = PrettyPrinter(indent = 4)
# PDF FORMATTING PARAMETER
CHAR_LIM = 74  # character limit of one line (max: 74)
LINE_LIM = 54  # Lines limit of one page (max: 54) reduce in steps of 3
TITLE_SIZE = 24  # Font size of the title (max: 24)
FONT_SIZE = 13.4  # Font size of the text (max: 13.4)
PDF_W = 215  # Width of the pdf text field (min 215)
PDF_H = 5.28  # Height for each pdf line (5.18 - 5.28)
PATH_NOTO = './fonts/NotoMono.ttf'
NEW_LINE = '\n'
# TEXT DECODING PARAMETER
PATTERNS = [',', ';', '.', ':', '!', '?']
PUNCTUATIONS = ['.', '!', '?']

# Dictionary of common translation mistakes. (Example for russian to german)
DICTIONARY = {
    'ICH BIN': 'Ich', 'Ich bin': 'Ich', 'ich bin': 'ich', 'ICH': 'Ich', 'DU BIST': 'Du', 'Du bist': 'Du', 'du bist': 'du',
    'ER IST': 'Er', 'Er ist': 'Er', 'er ist': 'er', 'SIE IST': 'Sie', 'Sie ist': 'Sie', 'sie ist': 'sie',
    'ES IST': 'Es', 'Es ist': 'Es', 'es ist': 'es', 'WIR SIND': 'Wir', 'Wir sind': 'Wir', 'wir sind': 'wir',
    'IHR SEID': 'Ihr', 'Ihr seid': 'Ihr', 'ihr seid': 'ihr', 'SIE SIND': 'Sie', 'Sie sind': 'Sie', 'sie sind': 'sie',
    'BIN ICH': 'Ich', 'Bin ich': 'Ich', 'bin ich': 'ich', 'BIST DU': 'Du', 'Bist du': 'Du', 'bist du': 'du',
    'IST ER': 'Er', 'Ist er': 'Er', 'ist er': 'er', 'IST SIE': 'Sie', 'Ist sie': 'Sie', 'ist sie': 'sie',
    'IST ES': 'Es', 'Ist es': 'Es', 'ist es': 'es', 'SIND WIR': 'Wir', 'Sind wir': 'Wir', 'sind wir': 'wir',
    'SEID IHR': 'Ihr', 'Seid ihr': 'Ihr', 'seid ihr': 'ihr', 'SIND SIE': 'Sie', 'Sind sie': 'Sie', 'sind sie': 'sie',
    'Für dich': 'Euch', 'für dich': 'euch', 'Dein sein': 'Euer', 'dein sein': 'euer', 'Es gibt': 'sein',
    'Verfügen über': 'Bei', 'beim': 'bei', 'Beim': 'Bei', 'ZU': 'Zu', 'Zu': 'zu', 'V': 'In', 'v': 'in', 'Ö': 'über', 'ö': 'über',
    'UND': 'Und', 'EIN': 'Und', 'ABER': 'Und', 'MIT': 'Mit', 'Mit': 'mit', 'Pro': 'Für', 'pro': 'für', 'von diesen': 'diese', 'BEI': 'In',
    'ABER)': 'A)', 'BEIM': 'In', 'Std': 'Stunde', 'Std.': 'Stunde', 'Auf der': 'Auf', 'auf der': 'auf', 'Jede einzelne': 'Jede', 'jede einzelne': 'jede',
    'Sie sagen': 'sprechen', '-': 'STRICH', 'STRICH': '-'
}


class LanguageDecoder(object):

    def __init__(self, source_language: str = 'auto', target_language: str = 'en',
                 word_space: int = 4, page_sep: bool = False):
        self.translator = GoogleTranslator(source = source_language, target = target_language)
        self.word_space = word_space
        self.page_sep = ''
        self.char_lim = CHAR_LIM
        if page_sep:
            self.page_sep = '|'
            self.char_lim = CHAR_LIM - 1
        self.fpdf = None

    def __init_fpdf__(self):
        self.fpdf = FPDF(format = 'A4', orientation = 'P', unit = 'mm')
        self.fpdf.add_font(family = 'Noto', fname = PATH_NOTO, uni = True)
        self.fpdf.set_auto_page_break(auto = False, margin = 0)
        self.fpdf.set_margins(left = -1, top = 1, right = -1)

    def get_supported_languages(self) -> List[str]:
        languages = self.translator.get_supported_languages(as_dict = True)
        pp.pprint(languages)
        return list(languages.values())

    def _translate(self, text: str) -> str:
        try:
            return self.translator.translate(text)
        except RequestError as exception:
            print('Connection Error')
            print(exception)
        except TooManyRequests as exception:
            print('To Many Requests')
            print(exception)
        except MicrosoftAPIerror as exception:
            print('Microsoft API Error')
            print(exception)
        except Exception as exception:
            print('Unexpected Error')
            print(exception)
            return ''

    def _translate_batch(self, batch: List[str]) -> List[str]:
        try:
            return self.translator.translate_batch(batch)
        except RequestError as exception:
            print('Connection Error')
            print(exception)
        except TooManyRequests as exception:
            print('To Many Requests')
            print(exception)
        except MicrosoftAPIerror as exception:
            print('Microsoft API Error')
            print(exception)
        except Exception as exception:
            print('Unexpected Error')
            print(exception)
            return ['']

    @staticmethod
    def _text_formatting(text: str, patterns: list, addons: list = None, reduces: list = None) -> str:
        text = ' '.join(text.split())  # remove whitespaces
        # add whitespaces if char starts with uppercase
        # text = ''.join([f' {char}' if char.isupper() else char for char in text])
        if reduces:
            if len(patterns) == len(reduces):
                for pattern, reduce in zip(patterns, reduces):
                    text = text.replace(reduce + pattern, pattern)
            else:
                reduce = reduces[0]
                for pattern in patterns:
                    text = text.replace(reduce + pattern, pattern)
        if addons:
            if len(patterns) == len(addons):
                for pattern, addon in zip(patterns, addons):
                    text = text.replace(pattern, pattern + addon)
            else:
                addon = addons[0]
                for pattern in patterns:
                    text = text.replace(pattern, pattern + addon)
        return ' '.join(text.split())  # remove whitespaces

    @staticmethod
    def _replace_words(word_list: list) -> List[str]:
        return [DICTIONARY.get(word) if word in DICTIONARY.keys() else word for word in word_list]

    @staticmethod
    def _lonlen(a_list: list) -> int:
        return len(max(a_list, key = len))

    @staticmethod
    def _get_decode_paths(source_path: str) -> Tuple[str, str]:
        if not os.path.isfile(source_path):
            raise OSError('Error in `LanguageDecoder.decode_text´. Text file not Found. ')
        title = os.path.basename(source_path).split('.')[0]
        decode_path = os.path.join(os.path.dirname(source_path), title + '_decode.txt')
        transl_path = os.path.join(os.path.dirname(source_path), title + '_transl.txt')
        return decode_path, transl_path

    @staticmethod
    def _get_pdf_paths(decode_path: str) -> Tuple[str, str]:
        if not os.path.isfile(decode_path):
            raise OSError('Error in `LanguageDecoder.decode_text´. Text file not Found. ')
        title = os.path.basename(decode_path).split('_')[0]
        pdf_path = os.path.join(os.path.dirname(decode_path), title + '.pdf')
        return pdf_path, title

    @staticmethod
    def delete_decoded_files(decode_path: str):
        transl_path = decode_path[:-len('decode.txt')] + 'transl.txt'
        if os.path.isfile(decode_path):
            os.remove(decode_path)
        if os.path.isfile(transl_path):
            os.remove(transl_path)

    def decode_text(self, source_path: str, translate_text: bool = False) -> Optional[str]:
        decode_path, transl_path = self._get_decode_paths(source_path = source_path)

        if os.path.isfile(decode_path):
            # print('Text already decoded: ', decode_path, '\n')
            return

            # read text file
        with open(file = source_path, mode = 'r', encoding = 'utf-8') as file:
            text = file.read()

        # formatting text for translator
        source_text = self._text_formatting(text = text, patterns = PATTERNS, addons = [' '], reduces = [' '])
        # split text into words
        source_words = source_text.split()
        if len(source_words) == 0:
            return
        print('Decode Text for:', source_path)
        print(f'Found {len(source_words)} words')
        words_batch = self._replace_words(word_list = source_words)
        decode_words = self._translate_batch(words_batch)
        decode_words = self._replace_words(word_list = decode_words)
        print('Decoded words!', '\n')

        # formatting text
        source_line = ''
        decode_line = ''
        decode_text = ''
        for source_word, decode_word in zip(source_words, decode_words):
            # add missing punctuation mark
            if source_word[-1] in PATTERNS and decode_word[-1] not in PATTERNS:
                decode_word += source_word[-1]
            # get the length of the longest word + space
            word_len = self._lonlen([source_word, decode_word]) + self.word_space
            # if a punctuation mark is at the end of the word (end of sentence)
            if any(punctuation == source_word[-1] for punctuation in PUNCTUATIONS):
                # adjust word for same length without space and add word to the line
                source_line += source_word.ljust(word_len - self.word_space, ' ')
                decode_line += decode_word.ljust(word_len - self.word_space, ' ')
                # replace the space with NEW_LINE and combine to formatted text
                source_line = source_line + NEW_LINE
                decode_line = decode_line + NEW_LINE
                decode_text += source_line + decode_line + NEW_LINE
                # reset length and lines
                source_line = ''
                decode_line = ''
            else:
                # adjust word for same length and add it to the line
                source_line += source_word.ljust(word_len, ' ')
                decode_line += decode_word.ljust(word_len, ' ')

        # save decoded text
        with open(file = decode_path, mode = 'w', encoding = 'utf-8') as file:
            file.write(decode_text)

        if translate_text:
            transl_text = self._translate(source_text)
            transl_text = textwrap.fill(transl_text, width = CHAR_LIM)
            # save translated text
            with open(file = transl_path, mode = 'w', encoding = 'utf-8') as file:
                file.write(transl_text)

        return decode_path

    def convert2pdf(self, decode_path: str) -> Optional[str]:
        pdf_path, title = self._get_pdf_paths(decode_path = decode_path)

        if os.path.isfile(pdf_path):
            # print('PDF already created: ', pdf_path, '\n')
            return
        print('Create PDF for: ', decode_path)

        # read text file as lines
        with open(file = decode_path, mode = 'r', encoding = 'utf-8') as file:
            lines = file.readlines()

        # split lines in source and decode
        source_words = list()
        decode_words = list()
        for l, line in enumerate(lines):  # noqa
            if l % 3 == 0:
                source_words += line.split()
            if l % 3 == 1:
                decode_words += line.split()

        # formatting text
        line_len = 0
        source_line = ''
        decode_line = ''
        pdf_lines = list()
        for source_word, decode_word in zip(source_words, decode_words):
            # get the length of the longest word + space
            word_len = self._lonlen([source_word, decode_word]) + self.word_space
            # get the length of the current line
            line_len += word_len
            # if the length of the line is to long
            if (line_len - self.word_space) > self.char_lim:
                # replace the space with NEW_LINE and append to pdf lines
                pdf_lines.append(source_line[0:-self.word_space] + NEW_LINE)
                pdf_lines.append(decode_line[0:-self.word_space] + NEW_LINE)
                pdf_lines.append(NEW_LINE)
                # reset length and lines
                line_len = word_len
                source_line = ''
                decode_line = ''
            # adjust word for same length and add it to the line
            source_line += source_word.ljust(word_len, ' ')
            decode_line += decode_word.ljust(word_len, ' ')
        # if the loop is finished create the last lines
        pdf_lines.append(source_line[0:-self.word_space] + NEW_LINE)
        pdf_lines.append(decode_line[0:-self.word_space] + NEW_LINE)
        pdf_lines.append(NEW_LINE)

        # create pages
        lines_len = len(pdf_lines)
        pages, completed_lines = list(), 0
        while completed_lines < lines_len:
            # get the lines for one page
            page_lines = pdf_lines[completed_lines:completed_lines + LINE_LIM]
            if len(pages) % 2:  # page number is odd
                # if page number is odd add page separator at the beginning of the line
                page_lines = [self.page_sep + line for line in page_lines]
            # join lines to a single page and remove the NEW_LINEs at the end of the page
            pages.append(''.join(page_lines)[:-2 * len(NEW_LINE)])
            completed_lines += LINE_LIM
        print(f'Convert {lines_len} lines of formatted text to pdf with {len(pages)} pages.', '\n')

        # formatting pdf
        first_page = True
        self.__init_fpdf__()
        pdf_title = f'    {title}'
        for p, page in enumerate(pages):
            self.fpdf.add_page()
            if first_page:
                # add the title to the top of the first front page
                self.fpdf.set_font(family = 'Noto', size = TITLE_SIZE)
                self.fpdf.cell(ln = 1, txt = pdf_title, align = 'L', w = PDF_W, h = PDF_H)
                self.fpdf.cell(ln = 1, txt = '', align = 'L', w = PDF_W, h = PDF_H)
                self.fpdf.cell(ln = 1, txt = '', align = 'L', w = PDF_W, h = PDF_H)
                self.fpdf.set_font(family = 'Noto', size = FONT_SIZE)
                first_page = False
            elif 0.5 * p % 2 < 1.:  # front page
                # add space to the top of the front page
                self.fpdf.set_font(family = 'Noto', size = FONT_SIZE)
                self.fpdf.cell(ln = 1, txt = '', align = 'L', w = PDF_W, h = PDF_H)
                self.fpdf.cell(ln = 1, txt = '', align = 'L', w = PDF_W, h = PDF_H)
                self.fpdf.cell(ln = 1, txt = '', align = 'L', w = PDF_W, h = PDF_H)
            # write the formatted page
            self.fpdf.multi_cell(txt = page, align = 'L', w = PDF_W, h = PDF_H)
            if 0.5 * p % 2 > 1.:  # back page
                # add space to the end of the back page
                self.fpdf.set_font(family = 'Noto', size = FONT_SIZE)
                self.fpdf.cell(ln = 1, txt = '', align = 'L', w = PDF_W, h = PDF_H)
                self.fpdf.cell(ln = 1, txt = '', align = 'L', w = PDF_W, h = PDF_H)
                self.fpdf.cell(ln = 1, txt = '', align = 'L', w = PDF_W, h = PDF_H)
        # create pdf
        self.fpdf.output(pdf_path)
        return pdf_path


if __name__ == "__main__":
    # Initialise language decoder.
    language_decoder = LanguageDecoder(source_language = 'ru', target_language = 'de')
    # Get supported languages.
    language_decoder.get_supported_languages()
    # Define source path to text file.
    source_path = '/../../.txt'
    # Decoding text (takes a while).
    decode_path = language_decoder.decode_text(source_path = source_path, translate_text = True)
    # Check the decoding translation before converting to pdf, because word by word translation is pretty bad.
    pdf_path = language_decoder.convert2pdf(decode_path = decode_path)
    # Optional remove decoded and translated text files.
    # language_decoder.delete_decoded_files(decode_path = decode_path)
