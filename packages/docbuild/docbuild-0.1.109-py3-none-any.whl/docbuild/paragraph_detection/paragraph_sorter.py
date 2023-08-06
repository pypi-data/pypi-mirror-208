import logging
from docstruct import Paragraph
from ..graph import Node, ParaGraph



def paragraph_comparator(first: Paragraph, second: Paragraph) -> int:
    """
    Returns 1 if the first paragraph is before the second paragraph.
    Returns -1 if the second paragraph is before the first paragraph.
    Returns 0 if there is no constraint.
    """
    first_bb = first.bounding_box
    second_bb = second.bounding_box

    "1 first < other. -1 first > other. 0 first intersect other."
    horizontal_relation = first_bb.get_horizontal_segment().relation(
        second_bb.get_horizontal_segment()
    )
    vertical_relation = -first_bb.get_vertical_segment().relation(
        second_bb.get_vertical_segment()
    )

    #! In case of intersection between the two paragraphs, there is no constraint between them.
    if horizontal_relation == 0 and vertical_relation == 0:
        return 0

    if horizontal_relation == 1 and vertical_relation == -1:
        return -1

    if horizontal_relation == -1 and vertical_relation == 1:
        return 1

    # At this point the horizontal and vertical agree up to intersection
    if abs(horizontal_relation) == 1:
        return horizontal_relation
    if abs(vertical_relation) == 1:
        return vertical_relation
    logging.error("Should not reach this line in the paragraph_comparator function")


def generate_paragraphs_graph(paragraphs: list[Paragraph]) -> ParaGraph:
    """
    Returns the adjacency list of the paragraphs graph.
    There is a directed edge between first paragraph to second paragraph if the first paragraph is before the second paragraph.
    """
    num_nodes = len(paragraphs)
    nodes = [Node(i) for i in range(num_nodes)]
    graph = ParaGraph(nodes=nodes, paragraphs=paragraphs)
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            relation = paragraph_comparator(paragraphs[i], paragraphs[j])
            if relation == 1:
                nodes[i].add_neighbor(nodes[j])
            elif relation == -1:
                nodes[j].add_neighbor(nodes[i])
    return graph


def sort_areas(paragraphs: list[Paragraph]) -> list[Paragraph]:
    """
    Sorts the paragraphs according to their order in the page.
    """
    graph: ParaGraph = generate_paragraphs_graph(paragraphs=paragraphs)
    sorted_paragraphs = graph.paragraph_sort()
    return [paragraphs[node] for node in sorted_paragraphs]
