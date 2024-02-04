import os
from typing import Optional, Tuple, List
from fpdf import FPDF
from backend.utils import utilities as utils


class PDF(object):

    def __init__(self,
                 font_path: str = '../fonts/NotoMono/NotoMono.ttf',
                 new_line: str = '\n',
                 word_space: int = 4,
                 page_sep: bool = False,
                 char_lim: int = 74,
                 line_lim: int = 54,
                 title_size: int = 24,
                 font_size: int = 13.4,
                 pdf_w: float = 215.,
                 pdf_h: float = 5.28) -> None:
        """
        :param font_path: path to the font used for the pdf (monospace font recommended)
        :param new_line: new line string
        :param word_space: the space between two words
        :param page_sep: optional pdf page seperator activation
        :param char_lim: character limit of one line (max: 74)
        :param line_lim: lines limit of one page (max: 54) reduce in steps of 3
        :param title_size: font size of the title (max: 24)
        :param font_size: font size of the text (max: 13.4)
        :param pdf_w: width of the pdf text field (min 215)
        :param pdf_h: height for each pdf line (5.18 - 5.28)
        """
        # super().__init__(orientation = 'P', unit = 'mm', format = 'A4')

        # self.add_font(family = 'Noto', fname = self.font_path, uni = True)
        # self.set_auto_page_break(auto = False, margin = 0)
        # self.set_margins(left = -1, top = 1, right = -1)

        self.font_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), font_path)
        self.new_line = new_line
        self.word_space = word_space
        self.page_sep = ''
        self.char_lim = char_lim
        if page_sep:
            self.page_sep = '|'
            self.char_lim -= 1
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

    @staticmethod
    def _get_pdf_paths(decode_path: str) -> Tuple[str, str]:
        if not os.path.isfile(decode_path):
            raise OSError('Error in `LanguageDecoder.decode_text´. Text file not Found.')
        title = os.path.basename(decode_path).split('_')[0]
        pdf_path = os.path.join(os.path.dirname(decode_path), f'{title}.pdf')
        return pdf_path, title

    def _read_decode_text(self, decode_path: str) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        pdf_path, title = self._get_pdf_paths(decode_path = decode_path)

        if os.path.isfile(pdf_path):
            # print(f'PDF already created: `{pdf_path}´\n')
            return None, None
        print(f'Create PDF for: `{decode_path}´.')

        # read text file as lines
        with open(file = decode_path, mode = 'r', encoding = 'utf-8') as file:
            lines = file.readlines()

        # split lines in source and decode
        source_words = list()
        decode_words = list()
        for i, line in enumerate(lines):
            if i % 3 == 0:
                source_words += line.split()
            if i % 3 == 1:
                decode_words += line.split()
        return source_words, decode_words

    def _format_text(self, source_words, decode_words) -> List[str]:
        line_len = 0
        source_line = ''
        decode_line = ''
        pdf_lines = list()
        for source_word, decode_word in zip(source_words, decode_words):
            # get the length of the longest word + word_space
            word_len = utils.lonlen([source_word, decode_word]) + self.word_space
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
        # pdf_lines.append(self.new_line)
        return pdf_lines

    def _create_pages(self, pdf_lines: List[str]) -> List[str]:
        lines_len = len(pdf_lines)
        pages, completed_lines = list(), 0
        while completed_lines < lines_len:
            # get the lines for one page
            page_lines = pdf_lines[completed_lines:completed_lines + self.line_lim]
            if len(pages) % 2:  # page number is odd
                # if page number is odd add page separator at the beginning of the line
                page_lines = [self.page_sep + line for line in page_lines]
            # join lines to a single page and remove the self.new_lines at the end of the page
            pages.append(''.join(page_lines)[:-len(self.new_line)])
            completed_lines += self.line_lim
        print(f'Convert {lines_len} lines of formatted text to pdf with {len(pages)} pages.\n')
        return pages

    def _format_pdf(self, title: str, pages: List[str]):
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

    def _delete_pkl_files(self):
        for file_path in os.listdir(os.path.dirname(self.font_path)):
            if file_path.endswith('.pkl'):
                os.remove(file_path)

    def convert2pdf(self, source_words: list = None, decode_words: list = None,
                    pdf_path: str = '', title: str = '', decode_path: str = '') -> Optional[str]:
        if decode_path:
            pdf_path, title = self._get_pdf_paths(decode_path = decode_path)
            source_words, decode_words = self._read_decode_text(decode_path = decode_path)
        if not source_words:
            return

        pdf_lines = self._format_text(source_words = source_words, decode_words = decode_words)
        pages = self._create_pages(pdf_lines = pdf_lines)
        self._format_pdf(title = title, pages = pages)
        # save pdf
        if not os.path.isfile(pdf_path) and pages:
            self._fpdf.output(pdf_path)
            self._delete_pkl_files()
            return pdf_path
