from lattice import Graph
from lattice import Node
from lattice import VisualEdge as Edge

grapha = Graph()
grapha.add_nodes(**{'0': Node(None, label='0')})
for i in range(1, 4):
    graphb = Graph()
    graphb.add_nodes(**{str(i): Node(None, label=str(i))})
    # create two copies of the original graph (they don't need to be added to the new graph)
    copya = Node(grapha.deepcopy())
    copyb = Node(grapha.deepcopy())

    # Add child edges
    graphb.get_node(str(i)).add_edge(Edge(), copya.data.get_node(str(i - 1)))
    graphb.get_node(str(i)).add_edge(Edge(), copyb.data.get_node(str(i - 1)))

    grapha = graphb

print(grapha)
