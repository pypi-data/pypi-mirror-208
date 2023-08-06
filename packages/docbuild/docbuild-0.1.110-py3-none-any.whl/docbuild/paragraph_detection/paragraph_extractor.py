import re
import attr

from docstruct import BoundingBox, Line, Paragraph
from ..constants import (
    PARAGRAPH_HORIZONTAL_SCALE,
    PARAGRAPH_HORIZONTAL_SCALE_FOR_LINES,
    PARAGRAPH_VERTICAL_SCALE,
    PARAGRAPH_VERTICAL_SCALE_FOR_LINES,
)
from ..graph import Graph, Node


@attr.s(auto_attribs=True)
class ParagraphIndexed:
    """
    Connected component of lines.
    """

    lines_indexes: list[int]
    bounding_box: BoundingBox


class ParagraphMerger:
    def __init__(self, paragraphs: list[ParagraphIndexed]):
        self.paragraphs = paragraphs
        self.num_nodes = len(paragraphs)
        self.graph: Graph = None

    def is_directed_edge(self, first_node: Node, second_node: Node):
        first_bb = self.paragraphs[first_node.data].bounding_box
        second_bb = self.paragraphs[second_node.data].bounding_box
        return first_bb.intersect(second_bb)

    def build_graph(self):
        nodes = [Node(i) for i in range(self.num_nodes)]
        self.graph = Graph(nodes)

        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                if self.is_directed_edge(nodes[i], nodes[j]):
                    nodes[i].add_neighbor(nodes[j])

    def merge_paragraphs(self) -> list[ParagraphIndexed]:
        self.build_graph()
        nodes = self.graph.nodes
        ccs: list[list[Node]] = self.graph.get_connected_components(nodes)
        merged_paragraphs: list[ParagraphIndexed] = []
        for cc in ccs:
            paragraph = self.merge_cc(cc)
            merged_paragraphs.append(paragraph)
        return merged_paragraphs

    def merge_cc(self, cc: list[Node]) -> ParagraphIndexed:
        lines_indexes = []
        bounding_boxes = []
        for node in cc:
            lines_indexes.extend(self.paragraphs[node.data].lines_indexes)
            bounding_boxes.append(self.paragraphs[node.data].bounding_box)
        bounding_box = BoundingBox.compose_bounding_boxes(bounding_boxes)
        return ParagraphIndexed(lines_indexes, bounding_box)


class ParagraphExtractor:
    def __init__(
        self,
        lines: list[Line],
        width_offset: int = 0,
        height_offset: int = 0,
        lines_segments: bool = False,
    ):
        self.lines = lines
        self.num_nodes = len(lines)
        self.graph: Graph = None
        if lines_segments is True:
            self.paragraph_horizontal_scale = PARAGRAPH_HORIZONTAL_SCALE_FOR_LINES
            self.paragraph_vertical_scale = PARAGRAPH_VERTICAL_SCALE_FOR_LINES
        else:
            self.paragraph_horizontal_scale = PARAGRAPH_HORIZONTAL_SCALE
            self.paragraph_vertical_scale = PARAGRAPH_VERTICAL_SCALE
        self.width_offset = width_offset
        self.height_offset = height_offset

    def build_graph(self):
        nodes = [Node(i) for i in range(self.num_nodes)]
        self.graph = Graph(nodes)
        nodes = sorted(
            nodes,
            key=lambda node: self.lines[node.data].get_bounding_box().get_center().y,
            reverse=True,
        )
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                if (
                    self.are_adjacent(nodes[i], nodes[j])
                    # and not self.is_indented(nodes[i], nodes[j])
                    and not self.is_bullet_number(nodes[j])
                ):
                    nodes[i].add_neighbor(nodes[j])
                    nodes[j].add_neighbor(nodes[i])

    def are_adjacent(self, first_node: Node, second_node: Node) -> bool:
        first_scaled_bb = self.lines[first_node.data].bounding_box.scale(
            width_scale=self.paragraph_horizontal_scale,
            height_scale=self.paragraph_vertical_scale,
            width_offset=self.width_offset,
            height_offset=self.height_offset,
        )
        second_scaled_bb = self.lines[second_node.data].bounding_box.scale(
            width_scale=self.paragraph_horizontal_scale,
            height_scale=self.paragraph_vertical_scale,
            width_offset=self.width_offset,
            height_offset=self.height_offset,
        )
        return first_scaled_bb.intersect(second_scaled_bb)

    def is_bullet_number(self, second_node: Node) -> bool:
        first_word_line_two = self.lines[second_node.data].get_children()[0]
        if bool(re.match("^\d{1,2}\.", first_word_line_two.get_text())) or bool(
            re.match("^\d{1,2}\)", first_word_line_two.get_text())
        ):
            return True
        return False

    def is_indented(self, first_node: Node, second_node: Node) -> bool:
        first_line_children = self.lines[first_node.data].get_children()
        first_word_line_two = (
            self.lines[second_node.data].get_children()[0].get_bounding_box()
        )
        indent = first_word_line_two.left
        count = 0
        for word in first_line_children:
            for char in word:
                if char.get_bounding_box().right < indent:
                    count += 1
                else:
                    if count > 3:
                        return True
                    return False
        return False

    def convert_ccs_to_paragraphs(
        self, ccs: list[list[Node]]
    ) -> list[ParagraphIndexed]:
        paragraphs = []
        for cc in ccs:
            lines_indexes = sorted([node.data for node in cc])
            bounding_boxes = [self.lines[i].bounding_box for i in lines_indexes]
            bounding_box = BoundingBox.compose_bounding_boxes(bounding_boxes)
            paragraphs.append(ParagraphIndexed(lines_indexes, bounding_box))
        return paragraphs

    def convert_paragraphs_indexed_to_paragraphs(
        self, paragraphs_indexed: list[ParagraphIndexed]
    ) -> list[Paragraph]:
        paragraphs = []
        for paragraph in paragraphs_indexed:
            lines = [self.lines[i] for i in paragraph.lines_indexes]
            paragraph = Paragraph(children=lines)
            paragraph.set_bounding_box()
            paragraphs.append(paragraph)
        return paragraphs

    def extract_paragraphs_temp(self) -> list[Paragraph]:
        if not self.lines:
            return []
        single_paragraph = Paragraph(children=self.lines)
        single_paragraph.set_bounding_box()
        return [single_paragraph]

    def extract_paragraphs(self) -> list[Paragraph]:
        if not self.lines:
            return []
        self.build_graph()
        ccs: list[list[Node]] = self.graph.get_connected_components()
        paragraphs: list[ParagraphIndexed] = self.convert_ccs_to_paragraphs(ccs)
        paragraph_merger = ParagraphMerger(paragraphs)
        merged_paragraphs: list[ParagraphIndexed] = paragraph_merger.merge_paragraphs()
        paragraphs = self.convert_paragraphs_indexed_to_paragraphs(merged_paragraphs)
        return paragraphs
