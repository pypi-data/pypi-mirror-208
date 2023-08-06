from lattice import Node
from lattice import VisualEdge as Edge
from lattice import BBTree, Graph

simple_graph = Graph()
node1 = "first"
node2 = "second"
node3 = "third"
node4 = "fourth"
simple_graph.add_nodes(node1=Node("first"))
simple_graph.add_nodes(node2=Node("second"))
simple_graph.add_nodes(node3=Node("third"))
simple_graph.add_nodes(node4=Node("fourth"))
simple_graph.get_node('node1').add_edge(Edge("c1"), simple_graph.get_node('node2'))
simple_graph.get_node('node2').add_edge(Edge("c2"), simple_graph.get_node('node1'))
simple_graph.get_node('node2').add_edge(Edge("c3"), simple_graph.get_node('node3'))
print(simple_graph)
# simple_graph.apply(lambda x: x + '_suffix')
# simple_graph.apply(print)

# simple_graph = Graph()
# node1 = Node(1)
# simple_graph.add_nodes(node1=node1)
# node11 = node1.copy()
# simple_graph.add_nodes(node11=node11)
# node2 = Node(2)
# node3 = Node(3)
# node4 = Node(4)
# simple_graph.get_node('node1').add_edge(Edge(), node2)
# node2.add_edge(Edge(), node3)
# node3.add_edge(Edge(), node4)
#
# def testfunc(x):
#     return x + 1
#
# def printfunc(x):
#     print(x)
#     return x
#
# simple_graph.apply(printfunc)
# simple_graph.apply(testfunc)
# print('\n\n\nAFTER APPLY \n\n\n')
# simple_graph.apply(printfunc)
