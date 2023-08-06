import itertools
import logging
import math
import cv2
from docstruct import Page, TextBlock, Word, Line, Paragraph, Table

from .textract_parser import TextractParser
from .paragraph_detection.paragraph_extractor import ParagraphExtractor
from .paragraph_detection.paragraph_sorter import sort_areas
from .visual_detection.bordered_table_extraction import BorderedTableExtractor
from .visual_detection.vis_line_detection import VisLineDetector
from .utils import get_average_character_height, get_average_character_width
from .constants import SORT_LINE_VERTICAL_SCALE

class PageCreator:
    def __init__(
        self,
        image_path: str,
        textract_response: dict = None,
        words: list[Word] = None,
        debug: bool = False,
    ):
        self.image_path = image_path
        self.textract_response = textract_response
        self.debug = debug
        self.words = words
        self.validate_args()

        self.image = cv2.imread(image_path)
        self.image_height, self.image_width = self.image.shape[:2]

    def validate_args(self):
        if self.textract_response is None and self.words is None:
            logging.error("Invalid arguments for PageCreator.")

    def extract_paragraphs(
        self,
        lines: list[Line],
        lines_segments: bool = False,
        height_offset: float = 0,
    ) -> list[Paragraph]:
        """
        Parse the paragraphs
        """
        paragraphs_extractor = ParagraphExtractor(
            lines=lines,
            height_offset=height_offset,
            lines_segments=lines_segments,
        )
        paragraphs = paragraphs_extractor.extract_paragraphs()
        return paragraphs

    def remove_table_words_from_lines(
        self, lines: list[Line], table_words: set[Word]
    ) -> list[Line]:
        """
        Remove the given words from the lines
        """
        non_empty_lines = []
        for line in lines:
            line_table_words = []
            for word in line.children:
                if word in table_words:
                    line_table_words.append(word)
            if not line_table_words:
                non_empty_lines.append(line)
                continue

            if len(line_table_words) == len(line.children):
                continue
            non_table_words = [
                word for word in line.children if word not in line_table_words
            ]
            line.set_children(non_table_words)
            line.set_length()
            line.set_bounding_box()
            non_empty_lines.append(line)
        return non_empty_lines

    def get_lines(
        self, words: list[Word], space_threshold: float
    ) -> list[Line]:
        """
        Parse the lines
        """
        words = sorted(words, key=lambda word: word.bounding_box.get_center().x)
        words = sorted(
            words,
            key=lambda word: word.bounding_box.get_center().y,
            reverse=True,
        )
        group_words = []
        start = 0

        for i in range(len(words) - 1):
            current_x = words[i].bounding_box.get_right()
            next_x = words[i + 1].bounding_box.get_left()
            current_ver_seg = words[i].bounding_box.get_vertical_segment()
            next_ver_seg = words[i + 1].bounding_box.get_vertical_segment()
            hor_condition = current_x < next_x < current_x + space_threshold
            ver_condition = current_ver_seg.intersect(next_ver_seg)
            if hor_condition and ver_condition:
                continue
            group_words.append(words[start : i + 1])
            start = i + 1
        group_words.append(words[start:])
        return [Line(children=group) for group in group_words]

    def get_tables(self, words: list[Word]) -> list[Table]:
        try:
            avg_word_size_ver = get_average_character_height(words) 
            avg_word_size_hor = (
                avg_word_size_ver * self.image_height / self.image_width
            )
            image_length_threshold = int(avg_word_size_ver * self.image_height)
            
            ver_threshold = avg_word_size_ver
            hor_threshold = avg_word_size_hor
            vis_line_detector = VisLineDetector(
                image_path=self.image_path, words=words
            )
            hor_lines, ver_lines = vis_line_detector.detect_lines(
                hor_threshold, ver_threshold, image_length_threshold
            )
            
            table_detector = BorderedTableExtractor(
                words,
                hor_lines,
                ver_lines,
                hor_threshold,
                ver_threshold,
            )

            tables = table_detector.detect_tables()
            return tables
        except Exception as e:
            logging.error(f"Error: {e}")
            return []

    def create_page(self) -> Page:

        if self.words is not None:
            words = self.words
            avg_char_width = get_average_character_width(words)
            lines = self.get_lines(words, space_threshold=3 * avg_char_width)

        else:
            parser = TextractParser(self.textract_response)
            lines = parser.parse_response()
            lines = TextBlock.sort(lines, height_scale = SORT_LINE_VERTICAL_SCALE)
            words = [word for line in lines for word in line.children]
        if not words:
            return Page()
        tables = self.get_tables(words)
        table_words = list(
            itertools.chain(*(table.get_all(Word) for table in tables))
        )
        lines = self.remove_table_words_from_lines(lines, set(table_words))
        lines_paragraphs = self.extract_paragraphs(
            lines=lines, lines_segments=True
        )
        height_offset = self.space_distribution(lines_paragraphs)
        paragraphs = self.extract_paragraphs(
            lines=lines, height_offset=height_offset
        )
        areas = paragraphs + tables
        areas = sort_areas(areas)
        page = Page(children=areas)
        page.set_bounding_box()
        page.set_length()
        return page

    @staticmethod
    def round_up(n: float, decimals: float = 0) -> float:
        multiplier = 10**decimals
        return math.ceil(n * multiplier) / multiplier

    @staticmethod
    def space_distribution(lines: list[Paragraph]) -> float:
        """
        Get the space distribution of the document
        """
        space_distribution = []
        paragraphs = list(lines)
        for i, paragraph in enumerate(paragraphs[:-1]):
            space = abs(
                paragraph.get_bounding_box().get_center().get_y()
                - paragraphs[i + 1].get_bounding_box().get_center().get_y()
            )
            space_distribution.append(space)

        space_distribution = sorted(space_distribution)
        total = sum(space_distribution)
        running_sum = 0
        for space in space_distribution:
            running_sum += space
            if running_sum / total >= 0.05:
                return PageCreator.round_up(space, 3)
        return 0
