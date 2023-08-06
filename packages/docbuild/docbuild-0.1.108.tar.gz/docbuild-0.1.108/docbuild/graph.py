from docstruct.text_block import Paragraph, TextBlock


class Node:
    def __init__(self, data: object):
        self.data: object = data
        self.neighbors: list[Node] = []

    def add_neighbor(self, neighbor: "Node"):
        self.neighbors.append(neighbor)

    def __str__(self):
        return f"{self.__class__.__name__}(data = {self.data})"

    def __repr__(self):
        return str(self)


class Graph:
    def __init__(self, nodes: list[Node]):
        self.nodes = nodes

    def get_connected_components(
        self, nodes_order: list[Node] = None
    ) -> list[list[Node]]:
        if nodes_order is None:
            nodes_order = self.nodes
        visited = set()
        connected_components: list[list[Node]] = []
        for node in nodes_order:
            if node not in visited:
                connected_component = self.get_connected_component(
                    node, visited
                )
                connected_components.append(connected_component)
        return connected_components

    def get_connected_component(
        self, node: Node, visited: set[Node]
    ) -> list[Node]:
        stack = [node]
        connected_component = []
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                connected_component.append(current)
                for neighbor in current.neighbors:
                    stack.append(neighbor)
        return connected_component

    @staticmethod
    def is_symmetric(graph: "Graph"):
        for node in graph.nodes:
            for neighbor in node.neighbors:
                if node not in neighbor.neighbors:
                    return False
        return True

    def get_nodes_with_bounded_degree(
        self, min_degree: int = 0, max_degree: int = -1
    ) -> list[Node]:
        if max_degree == -1:
            max_degree = len(self.nodes)
        nodes = []
        for node in self.nodes:
            if min_degree <= len(node.neighbors) <= max_degree:
                nodes.append(node)
        return nodes

    def remove_node(self, node: Node):
        """
        Remove a given node from the graph.
        For undirected graphs only!
        """

        for neighbor in node.neighbors:
            neighbor.neighbors.remove(node)
        node.neighbors = []
        self.nodes.remove(node)

    def topological_sort(self) -> list[Node]:
        num_nodes = len(self.nodes)
        in_degree = [0 for _ in range(num_nodes)]
        for node in range(num_nodes):
            for neighbor in self.nodes[node].neighbors:
                in_degree[neighbor.data] += 1
        queue = []
        for node in range(num_nodes):
            if in_degree[node] == 0:
                queue.append(self.nodes[node])

        sorted_nodes = []

        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)
            for neighbor in self.nodes[node.data].neighbors:
                in_degree[neighbor.data] -= 1
                if in_degree[neighbor.data] == 0:
                    queue.append(self.nodes[neighbor.data])
        if len(sorted_nodes) < num_nodes:
            raise Exception("Graph is not a DAG")
        return [node.data for node in sorted_nodes]


class BipartiteGraph(Graph):
    def __init__(self, left_nodes: list[Node], right_nodes: list[Node]):
        super().__init__(left_nodes + right_nodes)
        self.left_nodes = left_nodes
        self.right_nodes = right_nodes

    def remove_node(self, node: Node):
        super().remove_node(node)
        if node in self.left_nodes:
            self.left_nodes.remove(node)
        else:
            self.right_nodes.remove(node)


class ParaGraph(Graph):
    def __init__(self, nodes: list[Node], paragraphs: list[Paragraph]):
        super(ParaGraph, self).__init__(nodes)
        self.paragraphs = paragraphs
        first_lines = [paragraph.get_children()[0] for paragraph in paragraphs]
        pre_sort_paragraphs_indexes = TextBlock.sort(
            first_lines, return_indexes=True
        )
        self.pre_sort = [
            self.nodes[index] for index in pre_sort_paragraphs_indexes
        ]

    def paragraph_sort(self) -> list[Node]:
        num_nodes = len(self.nodes)
        in_degree = [0 for _ in range(num_nodes)]
        for node in range(num_nodes):
            for neighbor in self.nodes[node].neighbors:
                in_degree[neighbor.data] += 1
        queue = []
        for node in range(num_nodes):
            if in_degree[node] == 0:
                queue.append(self.nodes[node])
        if len(queue) == 0:
            queue.append(self.nodes[self.pre_sort[0].data])

        sorted_nodes = []

        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)
            for neighbor in self.nodes[node.data].neighbors:
                if neighbor not in sorted_nodes:
                    in_degree[neighbor.data] -= 1
                    if in_degree[neighbor.data] == 0:
                        queue.append(self.nodes[neighbor.data])

            if len(queue) == 0 and len(sorted_nodes) < num_nodes:
                for node in self.pre_sort:
                    if node not in sorted_nodes:
                        queue.append(self.nodes[node.data])
                        break
        return [node.data for node in sorted_nodes]
