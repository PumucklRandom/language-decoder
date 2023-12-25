import os
import re
import textwrap
from fpdf import FPDF
from typing import Optional, Tuple, List
from pprint import PrettyPrinter
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError, TooManyRequests, MicrosoftAPIerror
from dictionaries import PUNCTUATIONS, BEG_PATTERNS, END_PATTERNS, QUO_PATTERNS
from dictionaries import PLACEHOLDERS, CHARS, RU2DE


class LanguageDecoder(object):

    """
    The LanguageDecoder is used to translate a text from a source language to a given target language word by word (decoding).
    Therefor the Google translator is used to generate a decoded text file.
    After checking the decoded text file, the decoding can be converted to a pdf file.
    """

    def __init__(self,
                 source_language: str = 'auto',
                 target_language: str = 'en',
                 new_line: str = '\n',
                 word_space: int = 4,
                 char_lim_decode: int = 120,
                 replace_dict: dict = None,
                 dictionary: dict = None,
                 font_path: str = './fonts/NotoMono.ttf',
                 page_sep: bool = False,
                 char_lim: int = 74,
                 line_lim: int = 54,
                 title_size: int = 24,
                 font_size: int = 13.4,
                 pdf_w: float = 215.,
                 pdf_h: float = 5.28):

        """
        # TEXT DECODING PARAMETER
        :param source_language: the translation source language
        :param target_language: the translation target language
        :param new_line: new line string
        :param word_space: the space between two words
        :param char_lim_decode: character limit of one line for decode text file
        :param replace_dict: a dictionary to replace chars
        :param dictionary: a dictionary to correct common translation mistakes
        # PDF FORMATTING PARAMETER
        :param font_path: path to the font used for the pdf (monospace font recommended)
        :param page_sep: optional pdf page seperator activation
        :param char_lim: character limit of one line (max: 74)
        :param line_lim: lines limit of one page (max: 54) reduce in steps of 3
        :param title_size: font size of the title (max: 24)
        :param font_size: font size of the text (max: 13.4)
        :param pdf_w: width of the pdf text field (min 215)
        :param pdf_h: height for each pdf line (5.18 - 5.28)
        """

        self._pp = PrettyPrinter(indent = 4)
        self._translator = GoogleTranslator(source = source_language, target = target_language)
        self.source_language = source_language
        self.target_language = target_language
        self.new_line = new_line
        self.word_space = word_space
        self.char_lim_decode = char_lim_decode
        self.replace_dict = replace_dict
        if not isinstance(self.replace_dict, dict):
            self.replace_dict = dict()
        self.dictionary = dictionary
        if not isinstance(self.dictionary, dict):
            self.dictionary = dict()
        self.dictionary.update(PLACEHOLDERS)
        self.font_path = font_path
        self.page_sep = ''
        self.char_lim = char_lim
        if page_sep:
            self.page_sep = '|'
            self.char_lim = self.char_lim - 1
        self.line_lim = line_lim
        self.title_size = title_size
        self.font_size = font_size
        self.pdf_w = pdf_w
        self.pdf_h = pdf_h
        self._fpdf: FPDF

    def __init_fpdf__(self) -> FPDF:
        self._fpdf = FPDF(format = 'A4', orientation = 'P', unit = 'mm')
        self._fpdf.add_font(family = 'Noto', fname = self.font_path, uni = True)
        self._fpdf.set_auto_page_break(auto = False, margin = 0)
        self._fpdf.set_margins(left = -1, top = 1, right = -1)
        return self._fpdf

    def get_supported_languages(self) -> List[str]:
        languages = self._translator.get_supported_languages(as_dict = True)
        self._pp.pprint(languages)
        return list(languages.values())

    def translate(self, text: str) -> str:
        try:
            return self._translator.translate(text)
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

    def translate_batch(self, batch: List[str]) -> List[str]:
        try:
            return self._translator.translate_batch(batch)
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
    def _lonlen(a_list: list) -> int:
        # get the length of the longest list element
        return len(max(a_list, key = len))

    @staticmethod
    def _replace_words(word_list: List[str], dictionary: dict) -> List[str]:
        return [dictionary.get(word) if word in dictionary.keys() else word for word in word_list]

    @staticmethod
    def _get_decode_paths(source_path: str) -> Tuple[str, str]:
        if not os.path.isfile(source_path):
            raise OSError('Error in `LanguageDecoder.decode_text´. Text file not Found.')
        title = os.path.basename(source_path).split('.')[0]
        decode_path = os.path.join(os.path.dirname(source_path), f'{title}_decode.txt')
        transl_path = os.path.join(os.path.dirname(source_path), f'{title}_transl.txt')
        return decode_path, transl_path

    @staticmethod
    def _get_pdf_paths(decode_path: str) -> Tuple[str, str]:
        if not os.path.isfile(decode_path):
            raise OSError('Error in `LanguageDecoder.decode_text´. Text file not Found.')
        title = os.path.basename(decode_path).split('_')[0]
        pdf_path = os.path.join(os.path.dirname(decode_path), f'{title}.pdf')
        return pdf_path, title

    @staticmethod
    def delete_decoded_files(decode_path: str):
        transl_path = decode_path.replace('decode.txt', 'transl.txt')
        if os.path.isfile(decode_path):
            os.remove(decode_path)
        if os.path.isfile(transl_path):
            os.remove(transl_path)

    @staticmethod
    def _add_missing_marks(source_word: str, decode_word: str) -> str:
        # get the number of marks in the beginning of the word
        re_com = re.compile(f'^[{BEG_PATTERNS + QUO_PATTERNS}]*')
        beg_num_s = len(re.search(re_com, source_word).group())
        beg_num_d = len(re.search(re_com, decode_word).group())
        # get the number of marks in the end of the word
        re_com = re.compile(f'[{END_PATTERNS + QUO_PATTERNS}]*$')
        end_num_s = len(re.search(re_com, source_word).group())
        end_num_d = len(re.search(re_com, decode_word).group())
        # if the end numbers are 0 get the length of the words
        end_num_s = -len(source_word) if end_num_s == 0 else end_num_s
        end_num_d = -len(decode_word) if end_num_d == 0 else end_num_d
        # replace the marks in destin word from source word
        return f'{source_word[0:beg_num_s]}{decode_word[beg_num_d:-end_num_d]}{source_word[-end_num_s:]}'

    @staticmethod
    def _split_camel_case(text: str) -> str:
        # 'camelCase' -> 'camel. Case'
        i = 0
        end = len(text) - 1
        while i < end:
            if text[i].islower() and text[i + 1].isupper():
                text = f'{text[:i + 1]}. {text[i + 1:]}'
                i += 2
                end += 2
            i += 1
        return text

    def text_formatting(self, text: str) -> str:
        # remove superfluous whitespaces and new lines
        text = ' '.join(text.split())
        # replace special characters with common ones
        for char in self.replace_dict.keys():
            text = text.replace(char, self.replace_dict.get(char))
        # swap "quotation marks" with punctuations if quotation mark is followed by punctuation
        text = re.sub(f'([{QUO_PATTERNS}])\s*([{PUNCTUATIONS}])', r'\2\1', text)
        # remove any white whitespaces after "begin marks" and add one whitespace before "begin marks"
        text = re.sub(f'([{BEG_PATTERNS}])\s*', r' \1', text)
        # remove any white whitespaces before "end marks" and add one whitespace after "end marks"
        text = re.sub(f'\s*([{END_PATTERNS}])', r'\1 ', text)
        # remove whitespaces inside "quotation mark" pairs and add whitespaces outside of pairs
        text = re.sub(f'([{QUO_PATTERNS[0]}])\s*(.*?)\s*([{QUO_PATTERNS[0]}])', r' \1\2\3 ', text)
        text = re.sub(f'([{QUO_PATTERNS[1]}])\s*(.*?)\s*([{QUO_PATTERNS[1]}])', r' \1\2\3 ', text)
        text = re.sub(f'([{QUO_PATTERNS[2:]}])\s*(.*?)\s*([{QUO_PATTERNS[2:]}])', r' \1\2\3 ', text)
        # add potentially missing dots
        text = self._split_camel_case(text)
        # add a dot at the end of the text in case of missing punctuation
        if not any(punctuation in text.split()[-1] for punctuation in PUNCTUATIONS):
            text += '.'
        return ' '.join(text.split())

    def decode_text(self, source_path: str, translate_text: bool = False) -> Optional[str]:
        decode_path, transl_path = self._get_decode_paths(source_path = source_path)

        if os.path.isfile(decode_path):
            # print(f'Text already decoded: `{decode_path}´. \n')
            return

        # read text file
        with open(file = source_path, mode = 'r', encoding = 'utf-8') as file:
            text = file.read()

        if len(text) == 0:
            print('Text is empty.\n')
            return

        # formatting text for translator
        source_text = self.text_formatting(text = text)
        # split text into words
        source_words = source_text.split()
        print(f'Decode Text for: `{source_path}´.')
        print(f'Found {len(source_words)} words.')
        words_batch = self._replace_words(word_list = source_words, dictionary = PLACEHOLDERS)
        decode_words = self.translate_batch(words_batch)
        if len(decode_words) != len(source_words):
            print('Something went wrong with the translation.\n')
            return
        decode_words = self._replace_words(word_list = decode_words, dictionary = self.dictionary)
        print(f'Decoded words!\n')

        # formatting text
        line_len = 0
        source_line = ''
        decode_line = ''
        decode_text = ''
        for source_word, decode_word in zip(source_words, decode_words):
            decode_word = self._add_missing_marks(source_word = source_word, decode_word = decode_word)
            # get the length of the longest word + word_space
            word_len = self._lonlen([source_word, decode_word]) + self.word_space
            # get the length of the current line
            line_len += word_len
            # if the length of the line is too long
            if (line_len - self.word_space) > self.char_lim_decode:
                # add self.new_line at the end
                source_line = f'{source_line[0:-self.word_space]}{self.new_line}'
                decode_line = f'{decode_line[0:-self.word_space]}{self.new_line}'
                # combine to formatted text
                decode_text = f'{decode_text}{source_line}{decode_line}{self.new_line}'
                # set length to word length
                line_len = word_len
                # adjust word for same length, add word_space and add it to the line
                source_line = source_word.ljust(word_len, ' ')
                decode_line = decode_word.ljust(word_len, ' ')
            # if a punctuation mark is at the end of the word (end of sentence)
            elif any(punctuation in source_word for punctuation in PUNCTUATIONS):
                # add word to the line and add self.new_line at the end
                source_line = f'{source_line}{source_word}{self.new_line}'
                decode_line = f'{decode_line}{decode_word}{self.new_line}'
                # combine to formatted text
                decode_text = f'{decode_text}{source_line}{decode_line}{self.new_line}'
                # reset length and lines
                line_len = 0
                source_line = ''
                decode_line = ''
            else:
                # adjust word for same length, add word_space and add it to the line
                source_line += source_word.ljust(word_len, ' ')
                decode_line += decode_word.ljust(word_len, ' ')

        # save decoded text
        with open(file = decode_path, mode = 'w', encoding = 'utf-8') as file:
            file.write(decode_text)

        if translate_text:
            transl_text = self.translate(source_text)
            transl_text = textwrap.fill(transl_text, width = self.char_lim_decode)
            # save translated text
            with open(file = transl_path, mode = 'w', encoding = 'utf-8') as file:
                file.write(transl_text)

        return decode_path

    def convert2pdf(self, decode_path: str) -> Optional[str]:
        pdf_path, title = self._get_pdf_paths(decode_path = decode_path)

        if os.path.isfile(pdf_path):
            # print(f'PDF already created: `{pdf_path}´\n')
            return
        print(f'Create PDF for: `{decode_path}´.')

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
            # get the length of the longest word + word_space
            word_len = self._lonlen([source_word, decode_word]) + self.word_space
            # get the length of the current line
            line_len += word_len
            # if the length of the line is too long
            if (line_len - self.word_space) > self.char_lim:
                # replace the word_space with self.new_line and append to pdf lines
                pdf_lines.append(f'{source_line[0:-self.word_space]}{self.new_line}')
                pdf_lines.append(f'{decode_line[0:-self.word_space]}{self.new_line}')
                pdf_lines.append(self.new_line)
                # reset length and lines
                line_len = word_len
                source_line = ''
                decode_line = ''
            # adjust word for same length, add word_space and add it to the line
            source_line += source_word.ljust(word_len, ' ')
            decode_line += decode_word.ljust(word_len, ' ')
        # if the loop is finished create the last lines
        pdf_lines.append(f'{source_line[0:-self.word_space]}{self.new_line}')
        pdf_lines.append(f'{decode_line[0:-self.word_space]}{self.new_line}')
        pdf_lines.append(self.new_line)

        # create pages
        lines_len = len(pdf_lines)
        pages, completed_lines = list(), 0
        while completed_lines < lines_len:
            # get the lines for one page
            page_lines = pdf_lines[completed_lines:completed_lines + self.line_lim]
            if len(pages) % 2:  # page number is odd
                # if page number is odd add page separator at the beginning of the line
                page_lines = [self.page_sep + line for line in page_lines]
            # join lines to a single page and remove the self.new_lines at the end of the page
            pages.append(''.join(page_lines)[:-2 * len(self.new_line)])
            completed_lines += self.line_lim
        print(f'Convert {lines_len} lines of formatted text to pdf with {len(pages)} pages.\n')

        # formatting pdf
        first_page = True
        self.__init_fpdf__()
        pdf_title = f'    {title}'
        for p, page in enumerate(pages):
            self._fpdf.add_page()
            if first_page:
                # add the title to the top of the first front page
                self._fpdf.set_font(family = 'Noto', size = self.title_size)
                self._fpdf.cell(ln = 1, txt = pdf_title, align = 'L', w = self.pdf_w, h = self.pdf_h)
                self._fpdf.cell(ln = 1, txt = '', align = 'L', w = self.pdf_w, h = self.pdf_h)
                self._fpdf.cell(ln = 1, txt = '', align = 'L', w = self.pdf_w, h = self.pdf_h)
                self._fpdf.set_font(family = 'Noto', size = self.font_size)
                first_page = False
            elif 0.5 * p % 2 < 1.:  # front page
                # add space to the top of the front page
                self._fpdf.set_font(family = 'Noto', size = self.font_size)
                self._fpdf.cell(ln = 1, txt = '', align = 'L', w = self.pdf_w, h = self.pdf_h)
                self._fpdf.cell(ln = 1, txt = '', align = 'L', w = self.pdf_w, h = self.pdf_h)
                self._fpdf.cell(ln = 1, txt = '', align = 'L', w = self.pdf_w, h = self.pdf_h)
            # write the formatted page
            self._fpdf.multi_cell(txt = page, align = 'L', w = self.pdf_w, h = self.pdf_h)
            if 0.5 * p % 2 > 1.:  # back page
                # add space to the end of the back page
                self._fpdf.set_font(family = 'Noto', size = self.font_size)
                self._fpdf.cell(ln = 1, txt = '', align = 'L', w = self.pdf_w, h = self.pdf_h)
                self._fpdf.cell(ln = 1, txt = '', align = 'L', w = self.pdf_w, h = self.pdf_h)
                self._fpdf.cell(ln = 1, txt = '', align = 'L', w = self.pdf_w, h = self.pdf_h)
        # create pdf
        self._fpdf.output(pdf_path)
        return pdf_path


if __name__ == "__main__":
    # Initialise language decoder.
    language_decoder = LanguageDecoder(source_language = 'ru', target_language = 'de',
                                       replace_dict = CHARS, dictionary = RU2DE)
    # Get supported languages.
    language_decoder.get_supported_languages()
    # Define source path to text file.
    source_path = 'C:/Users/User/source/text.txt'
    # Decoding text (takes a while).
    decode_path = language_decoder.decode_text(source_path = source_path, translate_text = True)
    # Check the decoding translation manually before converting to pdf, because word by word translation is pretty bad!
    # Create a pdf file from the decoding
    pdf_path = language_decoder.convert2pdf(decode_path = decode_path)
    # Optional remove decoded and translated text files.
    # language_decoder.delete_decoded_files(decode_path = decode_path)
