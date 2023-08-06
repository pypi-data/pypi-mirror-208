from .graph import Graph
from ..edge.edge import Edge


class Tree(Graph):
    """
    A tree is a type of graph that constrains relationship types
    Trees are formally constrained as graphs where all nodes except the root must have one predecessor
    """

    def __init__(self, root_node, copy=True):
        super().__init__()
        if copy:
            self.root_node = root_node.copy()
        else:
            self.root_node = root_node
        self._nodes.add(self.root_node)

    def add_nodes(self, parent_node, edge: Edge, **kwargs):
        """
        A node must be added by specifying an existing node as a predecessor
        """
        for key, value in kwargs.items():
            new_node = value.copy(key)
            setattr(self, key, new_node)

            self.add_edge(parent_node, new_node, edge)
