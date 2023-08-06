from bs4 import BeautifulSoup, Tag
from docstruct import BoundingBox, Line, Page, Paragraph, Word
import re
from .constants import BBOX_PATTERN
import logging

class HocrParser:

    """
    This class is used to parse hocr files into a page structure.
    """

    def __init__(self, hocr_file_path: str):
        """
        Parameters:
        - hocr_file_path: the path to the hocr file
        - width: the width of the image the hocr file was generated from
        - height: the height of the image the hocr file was generated from
        """
        self.hocr_file_path = hocr_file_path
        self.soup = self.get_soup()
        self.width, self.height = self.get_page_size()

    def get_soup(self):
        """
        Returns the soup object of the hocr file.
        """
        with open(self.hocr_file_path, "r") as f:
            xml_data = f.read()
        soup = BeautifulSoup(xml_data, "html.parser")
        return soup

    def parse_left_top_right_bottom(
        self, tag: Tag
    ) -> tuple[float, float, float, float]:
        """
        Parses the bounding box of a tag.
        """
        title = tag["title"]
        match = re.search(BBOX_PATTERN, title)
        left, top, right, bottom = [float(x) for x in match.groups()]
        return left, top, right, bottom

    def get_bounding_box(self, tag: Tag) -> BoundingBox:
        # image coordinates
        left, top, right, bottom = self.parse_left_top_right_bottom(tag)

        # # normalized image coordinates
        left, top, right, bottom = (
            left / self.width,
            top / self.height,
            right / self.width,
            bottom / self.height,
        )

        # # normalized pdf coordinates
        top, bottom = 1 - top, 1 - bottom

        bounding_box = BoundingBox(left, top, right, bottom)
        return bounding_box

    def parse_word(self, word_tag: Tag) -> Word:
        """
        Parses a word from a tag.
        """
        bounding_box = self.get_bounding_box(word_tag)
        word = Word(bounding_box=bounding_box, text=word_tag.text)
        return word

    def parse_line(self, line_tag: Tag) -> Line:
        """
        Parses a line from a tag.
        """
        bounding_box = self.get_bounding_box(line_tag)
        line = Line(bounding_box=bounding_box)
        words = []
        words_tag = line_tag.find_all("span", class_="ocrx_word")
        if not words_tag:
            logging.error(
                "Found a line without words in hocr file %s",
                self.hocr_file_path,
            )
        for word_tag in words_tag:
            word = self.parse_word(word_tag)
            words.append(word)
        line.set_children(words)
        return line

    def parse_area(self, area_tag: Tag) -> Paragraph:
        """
        Parses a paragraph from a tag.
        Notice that the hocr file is structured as words, lines, paragraphs and areas.
        We build the Paragraph class out of what Tesseract consider as area!
        """

        bounding_box = self.get_bounding_box(area_tag)
        paragraph = Paragraph(bounding_box=bounding_box)
        lines = []
        lines_tag = area_tag.find_all("span", class_="ocr_line")
        captions_tag = area_tag.find_all("span", class_="ocr_caption")
        headers_tag = area_tag.find_all("span", class_="ocr_header")
        text_floats_tag = area_tag.find_all("span", class_="ocr_textfloat")
        all_tags = lines_tag + captions_tag + headers_tag + text_floats_tag

        for tag in all_tags:
            line = self.parse_line(tag)
            lines.append(line)
        paragraph.set_children(lines)
        return paragraph

    def get_page_size(self) -> tuple[float, float]:
        """
        Returns the image size from the hocr file.
        """
        page = self.soup.find("div", class_="ocr_page")
        left, top, right, bottom = self.parse_left_top_right_bottom(page)
        width = right - left
        height = bottom - top
        return width, height

    def parse_page(self):
        """
        Parses the page from the hocr file.
        """
        block_page = Page()

        captions = self.soup.find_all("div", class_="ocr_caption")

        # return
        areas_tag = self.soup.find_all("div", class_="ocr_carea")

        for area_tag in areas_tag:
            block_paragraph = self.parse_area(area_tag)
            block_page.add_child(block_paragraph)
        block_page.set_length()
        return block_page
