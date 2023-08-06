"""
This file serves as an example of building graphs within the capabilities of the code we have
"""
from lattice import Node
from lattice import TraverseEdge
from lattice import Edge
from lattice import BBTree, Graph

# Balanced Binary Tree
def build_binary_tree(n):
    graph = BBTree(Node(None, label=str(0)))
    for i in range(1, n + 1):
        graph.add_node(Node(None, label=str(i)))

    return graph


graph2 = build_binary_tree(20)

if __name__ == "__main__":
    # We have created several graphs, uncomment lines here to visualise them
    # graph1.visualise()
    # graph2.visualise()
    # print(graph1)
    # print(graph2)
    pass
