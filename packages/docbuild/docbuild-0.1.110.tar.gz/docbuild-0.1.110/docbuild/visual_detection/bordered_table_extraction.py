from typing import Optional
import attr
import numpy as np

from docstruct import Word, TableCell, Table, BoundingBox, Segment, VisLine, VisLineOrientation
from ..graph import Node, Graph, BipartiteGraph
from .constants import GRID_COVER_RATIO_THRESHOLD, IS_GRID_THRESHOLD


@attr.s(auto_attribs=True)
class CellOfLines:
    left: VisLine
    right: VisLine
    top: VisLine
    bottom: VisLine


class BorderedTableExtractor:
    def __init__(
        self,
        words: list[Word],
        hor_lines: list[VisLine],
        ver_lines: list[VisLine],
        hor_threshold: float,
        ver_threshold: float,
    ):
        self.words = words
        # top to bottom
        self.hor_lines = sorted(hor_lines, key=lambda line: line.axis, reverse=True)
        # left to right
        self.ver_lines = sorted(ver_lines, key=lambda line: line.axis)

        self.hor_threshold = hor_threshold
        self.ver_threshold = ver_threshold

    def group_lines_by_axis(
        self, lines: list[VisLine], length_threshold: float
    ) -> list[list[VisLine]]:
        """Assuming the lines are sorted by axis"""
        if not lines:
            return []
        grouped_lines = [[lines[0]]]

        for i in range(1, len(lines)):
            if abs(lines[i].axis - lines[i - 1].axis) > length_threshold:
                grouped_lines.append([lines[i]])
            else:
                grouped_lines[-1].append(lines[i])
        return grouped_lines

    def get_bipartite_graph(self):
        hor_nodes = []
        ver_nodes = []

        for hor_line in self.hor_lines:
            hor_nodes.append(Node(hor_line))

        for ver_line in self.ver_lines:
            ver_nodes.append(Node(ver_line))

        map_line_id_to_node = {}
        for node in hor_nodes:
            map_line_id_to_node[node.data.id] = node
        for node in ver_nodes:
            map_line_id_to_node[node.data.id] = node

        for hor_line in self.hor_lines:
            for ver_line in self.ver_lines:
                if self.are_adjacent_lines(hor_line, ver_line):
                    hor_node = map_line_id_to_node[hor_line.id]
                    ver_node = map_line_id_to_node[ver_line.id]
                    hor_node.add_neighbor(ver_node)
                    ver_node.add_neighbor(hor_node)

        bipartite_graph = BipartiteGraph(left_nodes=hor_nodes, right_nodes=ver_nodes)
        dummy_nodes = bipartite_graph.get_nodes_with_bounded_degree(
            min_degree=0, max_degree=1
        )
        for dummy_node in dummy_nodes:
            bipartite_graph.remove_node(dummy_node)
        return bipartite_graph

    def are_adjacent_lines(
        self,
        first_line: VisLine,
        second_line: VisLine,
    ):
        first_bb = first_line.convert_to_bb(
            length_threshold=0,
        )
        second_bb = second_line.convert_to_bb(
            length_threshold=0,
        )
        return first_bb.intersect(second_bb)

    def filter_lines_by_cycles(
        self, hor_nodes: list[Node], ver_nodes: list[Node]
    ) -> tuple[list[Node], list[Node]]:

        filtered_hor_nodes = set()
        filtered_ver_nodes = set()
        for top in hor_nodes:
            for j, left in enumerate(top.neighbors):
                for k in range(j + 1, len(top.neighbors)):
                    right = top.neighbors[k]
                    intersection_nodes = set(left.neighbors).intersection(
                        right.neighbors
                    )
                    if len(intersection_nodes) > 1:
                        filtered_hor_nodes.add(top)
                        filtered_ver_nodes.add(left)
                        filtered_ver_nodes.add(right)

        filtered_hor_nodes = list(filtered_hor_nodes)
        filtered_ver_nodes = list(filtered_ver_nodes)
        return filtered_hor_nodes, filtered_ver_nodes

    def detect_tables(self) -> list[Table]:
        bipartite_graph = self.get_bipartite_graph()
        connected_components = bipartite_graph.get_connected_components()
        tables = []
        for connected_component in connected_components:
            hor_nodes = [
                node
                for node in connected_component
                if node.data.orientation == VisLineOrientation.HORIZONTAL
            ]
            ver_nodes = [
                node
                for node in connected_component
                if node.data.orientation == VisLineOrientation.VERTICAL
            ]
            hor_nodes = sorted(hor_nodes, key=lambda node: node.data.axis, reverse=True)
            ver_nodes = sorted(ver_nodes, key=lambda node: node.data.axis)
            hor_cycle_nodes, ver_cycle_nodes = self.filter_lines_by_cycles(
                hor_nodes, ver_nodes
            )
            hor_cycle_nodes = [node.data for node in hor_nodes]
            ver_cycle_nodes = [node.data for node in ver_nodes]

            hor_cycle_lines = sorted(
                hor_cycle_nodes, key=lambda line: line.axis, reverse=True
            )
            ver_cycle_lines = sorted(ver_cycle_nodes, key=lambda line: line.axis)

            grouped_hor_lines = self.group_lines_by_axis(
                hor_cycle_lines, self.hor_threshold / 2
            )
            grouped_ver_lines = self.group_lines_by_axis(
                ver_cycle_lines, self.ver_threshold / 2
            )
            if len(grouped_hor_lines) < 2 or len(grouped_ver_lines) < 2:
                continue
            table_grid = TableGrid(grouped_hor_lines, grouped_ver_lines)

            table: Table = table_grid.detect_table(
                self.hor_lines, self.ver_lines, self.hor_threshold, self.ver_threshold
            )
            if table is None:
                continue
            table.group_words_into_cells(self.words)
            tables.append(table)

        return tables


class TableGrid:
    def __init__(
        self,
        grouped_hor_lines: list[list[VisLine]],
        grouped_ver_lines: list[list[VisLine]],
    ):
        self.grouped_hor_lines = grouped_hor_lines
        self.grouped_ver_lines = grouped_ver_lines

        self.m = len(grouped_hor_lines) - 1
        self.n = len(grouped_ver_lines) - 1

        self.hor_lines_grid = np.zeros((self.m + 1, self.n), dtype=bool)
        self.ver_lines_grid = np.zeros((self.m, self.n + 1), dtype=bool)

        self.hor_axis_values = self.get_axis_values(self.grouped_hor_lines)
        self.ver_axis_values = self.get_axis_values(self.grouped_ver_lines)

    def get_axis_values(self, grouped_lines: list[list[VisLine]]) -> list[float]:
        axis_values = []
        for lines in grouped_lines:
            axis = VisLine.get_weighted_average_axis(lines)
            axis_values.append(axis)
        return axis_values

    def fill_lines_grid(
        self, axis_values, all_lines_grouped: list[list[VisLine]], is_hor: bool
    ):  
        
        for k in range(len(all_lines_grouped)):
            segments = [
                Segment(left=line.start, right=line.end)
                for line in all_lines_grouped[k]
            ]
            for l in range(len(axis_values) - 1):
                grid_segment = Segment(
                    left=min(axis_values[l], axis_values[l + 1]),
                    right=max(axis_values[l], axis_values[l + 1]),
                )
                cover_ratio = grid_segment.proportion_covered_by_segments(segments)
                if cover_ratio > GRID_COVER_RATIO_THRESHOLD:
                    if is_hor:
                        self.hor_lines_grid[k][l] = True
                    else:
                        self.ver_lines_grid[l][k] = True

    def get_closest_index(self, value: float, values: list[float]) -> int:
        closest_index = -1
        min_diff = float("inf")
        for i, v in enumerate(values):
            diff = abs(value - v)
            if diff < min_diff:
                min_diff = diff
                closest_index = i
        return closest_index

    def group_lines_by_axis_values(
        self, axis_values: list[float], lines: list[VisLine], threshold: float
    ) -> list[list[VisLine]]:
        grouped_lines = [[] for _ in range(len(axis_values))]
        closest_axis_index = -1
        for line in lines:
            closest_axis_index = self.get_closest_index(line.axis, axis_values)
            distance = abs(line.axis - axis_values[closest_axis_index])
            if distance < threshold:
                grouped_lines[closest_axis_index].append(line)
        return grouped_lines

    def get_graph(self) -> Graph:
        """
        In this graph, each node represents a grid cell.
        Two nodes are connected if they are adjacent (plus)
        and there is no line between them.
        """
        nodes = []
        map_indexes_to_nodes = {}
        for i in range(self.m):
            for j in range(self.n):
                node = Node(data=(i, j))
                nodes.append(node)
                map_indexes_to_nodes[(i, j)] = node
        graph = Graph(nodes=nodes)
        for i in range(self.m):
            for j in range(self.n):
                current_node = map_indexes_to_nodes[(i, j)]
                for delta_y in (-1, 1):
                    if 0 <= i + delta_y < self.m:
                        neighbor_node = map_indexes_to_nodes[(i + delta_y, j)]
                        if not self.hor_lines_grid[i + delta_y][j]:
                            current_node.add_neighbor(neighbor_node)
                for delta_x in (-1, 1):
                    if 0 <= j + delta_x < self.n:
                        neighbor_node = map_indexes_to_nodes[(i, j + delta_x)]
                        if not self.ver_lines_grid[i][j + delta_x]:
                            current_node.add_neighbor(neighbor_node)
        return graph

    def get_cells(self, graph: Graph) -> list[TableCell]:
        connected_components = graph.get_connected_components()
        cells = []
        for component in connected_components:
            indexes = [node.data for node in component]
            min_i, max_i = (
                min(indexes, key=lambda x: x[0])[0],
                max(indexes, key=lambda x: x[0])[0],
            )
            min_j, max_j = (
                min(indexes, key=lambda x: x[1])[1],
                max(indexes, key=lambda x: x[1])[1],
            )
            if (max_i - min_i + 1) * (max_j - min_j + 1) == len(component):
                bounding_box = BoundingBox(
                    left=self.ver_axis_values[min_j],
                    right=self.ver_axis_values[max_j + 1],
                    top=self.hor_axis_values[min_i],
                    bottom=self.hor_axis_values[max_i + 1],
                )
                cell = TableCell(
                    bounding_box=bounding_box,
                    row_index=min_i,
                    col_index=min_j,
                    row_span=max_i - min_i + 1,
                    col_span=max_j - min_j + 1,
                )
                cells.append(cell)
            else:
                for node in component:
                    i, j = node.data
                    bounding_box = BoundingBox(
                        left=self.ver_axis_values[j],
                        right=self.ver_axis_values[j + 1],
                        top=self.hor_axis_values[i],
                        bottom=self.hor_axis_values[i + 1],
                    )
                    cell = TableCell(
                        bounding_box=bounding_box,
                        row_index=i,
                        col_index=j,
                        row_span=1,
                        col_span=1,
                    )
                    cells.append(cell)
        return cells
    
    @staticmethod
    def truth_ratio(matrix: np.ndarray) -> float:
        return np.count_nonzero(matrix) / matrix.size
    
    def is_grid(self):
        hor_cover = TableGrid.truth_ratio(self.hor_lines_grid)
        ver_cover = TableGrid.truth_ratio(self.ver_lines_grid)
        return hor_cover > IS_GRID_THRESHOLD and ver_cover > IS_GRID_THRESHOLD
    
    def detect_table(
        self,
        all_hor_lines: list[VisLine],
        all_ver_lines: list[VisLine],
        hor_threshold: float,
        ver_threshold: float,
    ) -> Optional[Table]:

        all_hor_lines_grouped = self.group_lines_by_axis_values(
            self.hor_axis_values, all_hor_lines, hor_threshold
        )
        all_ver_lines_grouped = self.group_lines_by_axis_values(
            self.ver_axis_values, all_ver_lines, ver_threshold
        )
        
        self.fill_lines_grid(self.ver_axis_values, all_hor_lines_grouped, is_hor=True)
        self.fill_lines_grid(self.hor_axis_values, all_ver_lines_grouped, is_hor=False)
        if not self.is_grid():
            return None
        graph = self.get_graph()
        cells = self.get_cells(graph)
        if len(cells) <= 1:
            return None
        return Table(cells=cells)
