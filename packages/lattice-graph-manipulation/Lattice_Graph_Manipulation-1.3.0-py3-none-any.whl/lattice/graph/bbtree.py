"""
A balanced binary tree is a type of graph that constrains nodes to have at most 2 children
Both the left and right side of the tree must have the same depth
We can also restructure the tree to allow for O(log(n)) search
"""
from .tree import Tree
from ..edge.edge import Edge


class BBTree(Tree):
    """
    Edges are inconsequential
    TODO: Current implementation creates an unbalanced tree, will probably have to look into a more clever solution for this
    """
    _frontier = []  # frontier queue defines which leaves should be added to next

    def __init__(self, root_node):
        root_node = root_node.copy(label=root_node.get_label())
        super().__init__(root_node, copy=False)
        self._frontier.append(root_node)
        self._frontier.append(root_node)

    def add_nodes(self, *nodes):
        """
        Allows adding multiple nodes at a time
        """
        for given_node in nodes:
            self.add_node(given_node)

    def add_node(self, node, **kwargs):
        """
        Nodes can only be added to the leaves of the tree
        We define the leaves as the frontier that can be added to
        """
        new_node = node.copy(label=node.get_label())
        leaf_node = self._frontier.pop(0)
        self._nodes.add(new_node)

        # Add the node to the frontier twice as the node can have 2 children
        self._frontier.append(new_node)
        self._frontier.append(new_node)

        # Finally add an edge between the leaf node and the new node
        self.add_edge(leaf_node, new_node, Edge())
