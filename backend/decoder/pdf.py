import os
import traceback
from typing import Union
from fpdf import FPDF
from backend.error.error import PDFFormatterError, catch
from backend.logger.logger import logger
from backend.utils import utilities as utils

file_dir = os.path.dirname(os.path.relpath(__file__))


class PDF(object):

    def __init__(self,
                 font_path: str = '../fonts/RobotoMono/RobotoMono.ttf',
                 new_line: str = '\n',
                 pages_per_sheet: int = 2,
                 page_sep: bool = False,
                 tab_size: int = 4,
                 char_lim: int = 75,
                 line_lim: int = 54,
                 top_margin: float = 0.3,
                 left_margin: float = -0.8,
                 title_size: float = 24,
                 font_size: float = 13.25,
                 title_height: float = 9.6,
                 line_height: float = 5.3,
                 width: float = 215.) -> None:

        """
        :param font_path: path to the font used for the pdf (monospace font recommended)
        :param new_line: new line string
        :param pages_per_sheet: number of pages per sheet
        :param page_sep: optional pdf page seperator activation
        :param tab_size: the tab size between two words
        :param char_lim: character limit of one line (max: 75)
        :param line_lim: lines limit of one page (max: 54) reduce in steps of 3
        :param top_margin: top margin of the pdf (edge at 0)
        :param left_margin: left margin of the pdf (edge at -1)
        :param title_size: font size of the title (max: 24)
        :param font_size: font size of the text (max: 13.2)
        :param title_height: height for the pdf title (max 10.2)
        :param line_height: height for each pdf line (5.3)
        :param width: width of the pdf text field (min 215)
        """

        self.font_path = os.path.join(file_dir, font_path)
        self.new_line = new_line
        self.pages_per_sheet = pages_per_sheet
        self.page_sep = '|' if page_sep else ''
        self.tab_size = tab_size
        self.char_lim = char_lim - (1 if page_sep else 0)
        self.line_lim = int(line_lim / 3) * 3
        self.title_size = title_size
        self.font_size = font_size
        self.top_margin = top_margin
        self.left_margin = left_margin
        self.title_height = title_height
        self.line_height = line_height
        self.width = width
        self._fpdf: FPDF

    def __init_fpdf__(self) -> FPDF:
        self._fpdf = FPDF(format = 'A4', orientation = 'P', unit = 'mm')
        self._fpdf.add_font(family = 'Noto', fname = self.font_path)
        self._fpdf.set_auto_page_break(auto = False, margin = 0)
        self._fpdf.set_margins(top = self.top_margin, left = self.left_margin)
        return self._fpdf

    def _format_lines(self, source_words: list[str], target_words: list[str]) -> list[str]:
        line_len = 0
        source_line = ''
        target_line = ''
        pdf_lines = list()
        for source_word, target_word in zip(source_words, target_words):
            # get the length of the longest word + word_space
            word_len = utils.maxlen([source_word, target_word]) + self.tab_size
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
        return pdf_lines

    def _format_pages(self, pdf_lines: list[str]) -> list[str]:
        lines_len = len(pdf_lines)
        pages, completed_lines = list(), 0
        while completed_lines < lines_len:
            # get the lines for one page
            page_lines = pdf_lines[completed_lines:completed_lines + self.line_lim]
            if self.page_sep and len(pages) % 2:  # page number is odd
                # if page number is odd add page separator at the beginning of the line
                page_lines = [self.page_sep + line for line in page_lines]
            # join lines to a single page and remove the self.new_lines at the end of the page
            pages.append(''.join(page_lines)[:-len(self.new_line)])
            completed_lines += self.line_lim
        return pages

    def _format_pdf(self, title: str, pdf_pages: list[str]) -> None:
        try:
            self.__init_fpdf__()
            pdf_title = f'    {title}'
            header_height = self.line_height * 3
            pps = 1 / self.pages_per_sheet if self.pages_per_sheet else 0
            for p, page in enumerate(pdf_pages):
                self._fpdf.add_page()
                if p == 0:
                    # add the title to the top of the first front page
                    self._fpdf.set_font(family = 'Noto', size = self.title_size)
                    self._fpdf.cell(text = pdf_title, w = self.width, h = self.title_height,
                                    new_x = 'LMARGIN', new_y = 'NEXT')
                    self._fpdf.cell(text = '', w = self.width, h = header_height - self.title_height,
                                    new_x = 'LMARGIN', new_y = 'NEXT')
                    # write formatted page
                    self._fpdf.set_font(family = 'Noto', size = self.font_size)
                    self._fpdf.multi_cell(text = page, w = self.width, h = self.line_height)
                elif pps * p % 2 < 1.:  # front pages
                    # add space to the top of the front pages
                    self._fpdf.cell(text = '', w = self.width, h = header_height,
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

    @catch(PDFFormatterError)
    def convert2pdf(self, title: str = '', source_words: list[str] = None,
                    target_words: list[str] = None) -> Union[None, bytes, str]:
        pdf_lines = self._format_lines(source_words = source_words, target_words = target_words)
        pdf_pages = self._format_pages(pdf_lines = pdf_lines)
        logger.info(f'Formatted PDF file with {len(pdf_pages)} pages.')
        self._format_pdf(title = title, pdf_pages = pdf_pages)
        # return pdf as bytes
        return bytes(self._fpdf.output())
