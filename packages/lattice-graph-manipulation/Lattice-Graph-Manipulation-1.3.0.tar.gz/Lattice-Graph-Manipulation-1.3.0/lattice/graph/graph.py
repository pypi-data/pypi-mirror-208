"""
The main focal data type of the project

NOTES:
    Edges have two options - Node.successor -> next node, edge
                             Node.successor -> edge -> next node
    We choose the first one as we can avoid the extra overhead and ensure
    That edges only exist within a graph

TODO:
- Find a more elegant way to reference nodes in a graph for operations such as finding edges
"""
import uuid
import os
from typing import List, Dict, Callable

import graphviz
from ..edge.visualedge import VisualEdge
from ..node.node import Node


class Graph:
    # A set of exposed nodes to access when they are called for (NOTE: may not include all nodes)
    _exposed_nodes: dict

    def __init__(self):
        self._nodes = {}  # initialise nodes as an empty set
        self.fingerprint = uuid.uuid4()

    @property
    def nodes(self) -> Dict[str, Node]:
        """Return the exposed nodes that belong to this graph """
        return self._nodes

    def add_nodes(self, **nodes: Node):
        """Exposed nodes are defined in key value pairs"""
        # add regular nodes
        for key, value in nodes.items():
            self._nodes[key] = value

    def add_node(self, node: Node, label):
        """Create a node within the graph"""
        self._nodes[label] = node

    def get_node(self, name: str):
        return self._nodes.get(name)

    def deepcopy(self):
        """Return a network of nodes encased by this graph, but copied"""
        new_graph = Graph()
        explored = {}
        for name, node in self.nodes.items():
            if node not in explored:
                new_node = node.copy(label=node.get_label())
                explored[node] = new_node
                new_graph.add_nodes(**{name: new_node})
                explored = self._recursive_copier(new_node, node, explored, new_graph)

        return new_graph

    def _recursive_copier(self, new_node, frontier_node, explored, graph):
        """Explore each new node and copy it into a given graph"""
        for edge, next_node in frontier_node.successors:
            if next_node not in explored:
                next_new_node = next_node.copy(label=next_node.get_label())
                explored[next_node] = next_new_node
                if next_node in self.nodes.values():
                    node_name = list(self._nodes.keys())[list(self._nodes.values()).index(next_node)]
                    graph.add_nodes(**{node_name: next_new_node})

                explored = self._recursive_copier(next_new_node, next_node, explored, graph)

            new_node.add_edge(edge, explored[next_node])
        return explored

    def visualise(self, fingerprint: str = None):
        """
        Display visible nodes in the graph
        Node names are set by the label of the node, rather than the key set by the graph
        """
        # Create a new fingerprint for each visualisation to generate a single file per print
        runtime_fingerprint = fingerprint or uuid.uuid4()
        dot = graphviz.Digraph(str(runtime_fingerprint))
        explored = []
        for name, node in self.nodes.items():
            if node not in explored:
                explored = self._recursive_visualiser(node, explored, dot)

        return dot

    def _recursive_visualiser(self, node: Node, explored: List[Node], dot):
        """Visualise every node by exploring node connections"""
        explored.append(node)
        shape = 'circle'
        if node in self._nodes.values():
            shape = 'doublecircle'
        dot.node(str(node), node.get_label(), shape=shape)
        for edge, next_node in node.successors:
            if isinstance(edge, VisualEdge):
                dot.edge(str(node), str(next_node), label=str(edge.get_label()))
                if next_node not in explored:
                    explored = self._recursive_visualiser(next_node, explored, dot)

        return explored

    def apply(self, func):
        """Apply a function flatly to every node in the network"""
        explored = []
        for node in self.nodes.values():
            if node not in explored:
                explored = self._recursive_apply(node, func, explored)

    def _recursive_apply(self, node: Node, func: Callable, explored: List[Node]):
        """Apply the function to this node then call this function on every connected node"""
        explored.append(node)
        node.data = func(node.data)
        for edge, next_node in node.successors:
            if next_node not in explored:
                self._recursive_apply(next_node, func, explored)

        return explored

    def __repr__(self):
        graphoutput = self.visualise()
        dotoutput = graphoutput.pipe(format='dot', encoding='utf-8')
        os.system('echo \'' + dotoutput + '\' | graph-easy --from=dot --as_ascii')
        # graphoutput.render(view=True)
        return "​"
