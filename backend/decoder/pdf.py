import os
import traceback
from typing import Optional, Tuple, List, Union
from fpdf import FPDF
from backend.error.error import PDFFormatterError
from backend.logger.logger import logger
from backend.utils import utilities as utils


class PDF(object):

    def __init__(self,
                 font_path: str = '../fonts/NotoMono/NotoMono.ttf',
                 new_line: str = '\n',
                 page_sep: bool = False,
                 tab_size: int = 4,
                 char_lim: int = 75,
                 line_lim: int = 54,
                 title_size: float = 24,
                 font_size: float = 13.2,
                 width: float = 215.,
                 title_height: float = 6.2,
                 header_height: float = 14.2,
                 line_height: float = 5.3) -> None:

        """
        :param font_path: path to the font used for the pdf (monospace font recommended)
        :param new_line: new line string
        :param page_sep: optional pdf page seperator activation
        :param tab_size: the tab size between two words
        :param char_lim: character limit of one line (max: 75)
        :param line_lim: lines limit of one page (max: 54) reduce in steps of 3
        :param title_size: font size of the title (max: 24)
        :param font_size: font size of the text (max: 13.2)
        :param width: width of the pdf text field (min 215)
        :param title_height: height for the pdf title (max 6.2)
        :param header_height: height for the pdf header/footer (14.2)
        :param line_height: height for each pdf line (5.3)
        """

        self.font_path = os.path.join(os.path.dirname(os.path.relpath(__file__)), font_path)
        self.new_line = new_line
        self.page_sep = ''
        self.tab_size = tab_size
        self.char_lim = char_lim
        if page_sep:
            self.page_sep = '|'
            self.char_lim -= 1
        self.line_lim = int(line_lim / 3) * 3
        self.title_size = title_size
        self.font_size = font_size
        self.width = width
        self.title_height = title_height
        self.header_height = header_height
        self.line_height = line_height
        self._fpdf: FPDF

    def __init_fpdf__(self) -> FPDF:
        self._fpdf = FPDF(format = 'A4', orientation = 'P', unit = 'mm')
        self._fpdf.add_font(family = 'Noto', fname = self.font_path)
        self._fpdf.set_auto_page_break(auto = False, margin = 0)
        self._fpdf.set_margins(left = -0.8, top = 2, right = -1)
        return self._fpdf

    def _format_lines(self, source_words, target_words) -> List[str]:
        try:
            line_len = 0
            source_line = ''
            target_line = ''
            pdf_lines = list()
            for source_word, target_word in zip(source_words, target_words):
                # get the length of the longest word + word_space
                word_len = utils.lonlen([source_word, target_word]) + self.tab_size
                # get the length of the current line
                line_len += word_len
                # if the length of the line is too long
                if (line_len - self.tab_size) > self.char_lim:
                    # replace the word_space with self.new_line and append to pdf lines
                    pdf_lines.append(f'{source_line[0:-self.tab_size]}{self.new_line}')
                    pdf_lines.append(f'{target_line[0:-self.tab_size]}{self.new_line}')
                    pdf_lines.append(self.new_line)
                    # reset length and lines
                    line_len = word_len
                    source_line = ''
                    target_line = ''
                # adjust word for same length, add word_space and add it to the line
                source_line += source_word.ljust(word_len, ' ')
                target_line += target_word.ljust(word_len, ' ')
            # if the loop is finished create the last lines
            pdf_lines.append(f'{source_line[0:-self.tab_size]}{self.new_line}')
            pdf_lines.append(f'{target_line[0:-self.tab_size]}{self.new_line}')
            # pdf_lines.append(self.new_line)
        except Exception:
            message = f'Could not format pdf lines with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise PDFFormatterError(message)
        return pdf_lines

    def _format_pages(self, pdf_lines: List[str]) -> List[str]:
        try:
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
        except Exception:
            message = f'Could not format pdf pages with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise PDFFormatterError(message)
        return pages

    def _format_pdf(self, title: str, pdf_pages: List[str]) -> None:
        try:
            first_page = True
            self.__init_fpdf__()
            pdf_title = f'    {title}'
            for p, page in enumerate(pdf_pages):
                self._fpdf.add_page()
                if first_page:
                    first_page = False
                    # add the title to the top of the first front page
                    self._fpdf.set_font(family = 'Noto', size = self.title_size)
                    self._fpdf.cell(text = pdf_title, w = self.width, h = self.title_height,
                                    new_x = 'LMARGIN', new_y = 'NEXT')
                    self._fpdf.cell(text = '', w = self.width, h = self.header_height - self.title_height,
                                    new_x = 'LMARGIN', new_y = 'NEXT')
                    # write formatted page
                    self._fpdf.set_font(family = 'Noto', size = self.font_size)
                    self._fpdf.multi_cell(text = page, w = self.width, h = self.line_height)
                elif 0.5 * p % 2 < 1.:  # front pages
                    # add space to the top of the front page
                    self._fpdf.cell(text = '', w = self.width, h = self.header_height,
                                    new_x = 'LMARGIN', new_y = 'NEXT')
                    # write formatted page
                    self._fpdf.multi_cell(text = page, w = self.width, h = self.line_height)
                else:  # back pages
                    # write formatted page
                    self._fpdf.multi_cell(text = page, w = self.width, h = self.line_height)
        except Exception:
            message = f'Could not format pdf file with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise PDFFormatterError(message)

    def convert2pdf(self, title: str = '', source_words: list = None, target_words: list = None,
                    decode_path: str = '') -> Union[None, bytes, str]:
        try:
            pdf_path = None
            if decode_path:
                pdf_path, title = self._get_pdf_paths(decode_path = decode_path)
                source_words, target_words = self._read_decode_text(decode_path = decode_path)
            if not source_words:
                return

            pdf_lines = self._format_lines(source_words = source_words, target_words = target_words)
            pdf_pages = self._format_pages(pdf_lines = pdf_lines)
            logger.info(f'Formatted PDF file with {len(pdf_pages)} pages.\n')
            self._format_pdf(title = title, pdf_pages = pdf_pages)

            if not pdf_path:
                # return pdf as bytes
                buffer = bytes(self._fpdf.output())
                return buffer

            if not os.path.isfile(pdf_path):
                # save pdf as file
                self._fpdf.output(pdf_path)
                return pdf_path

        except Exception:
            message = f'Could not convert words to pdf with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise PDFFormatterError(message)

    ####################################################################################################
    # Methods for backend only
    ####################################################################################################

    @staticmethod
    def _get_pdf_paths(decode_path: str) -> Tuple[str, str]:
        if not os.path.isfile(decode_path):
            message = f'Text file not found at "{decode_path}"'
            logger.error(message)
            raise PDFFormatterError(message)
        title = os.path.basename(decode_path).split('_')[0]
        pdf_path = os.path.join(os.path.dirname(decode_path), f'{title}.pdf')
        return pdf_path, title

    def _read_decode_text(self, decode_path: str) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        try:
            pdf_path, _ = self._get_pdf_paths(decode_path = decode_path)

            if os.path.isfile(pdf_path):
                # logger.info(f'PDF already created at: "{pdf_path}"')
                return None, None
            logger.info(f'Create PDF for: `{decode_path}´.')

            try:
                # read text file as lines
                with open(file = decode_path, mode = 'r', encoding = 'utf-8') as file:
                    lines = file.readlines()
            except IOError as exception:
                message = f'Could not open file at "{decode_path}" with exception:\n{traceback.format_exc()}'
                logger.error(message)
                raise PDFFormatterError(message)
            # split lines in source and decode
            source_words = list()
            target_words = list()
            for i, line in enumerate(lines):
                if i % 3 == 0:
                    source_words += line.split()
                if i % 3 == 1:
                    target_words += line.split()
            return source_words, target_words
        except Exception:
            message = f'Could not parse decoded text file with exception:\n{traceback.format_exc()}'
            logger.error(message)
            raise PDFFormatterError(message)
