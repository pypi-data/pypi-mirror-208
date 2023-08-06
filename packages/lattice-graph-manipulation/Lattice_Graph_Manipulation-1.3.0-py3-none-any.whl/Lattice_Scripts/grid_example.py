from lattice import Graph
from lattice import Node
from lattice import VisualEdge as Edge
import itertools

# base node setup
graph = Graph()
root_node = Node(None, label='0')
graph.add_nodes(**{'0': root_node})
vfront = [root_node]  # vertical frontier
hfront = [root_node]  # horizontal frontier

for i in range(1, 6):
    # refresh frontier
    new_vfront = []
    new_hfront = []

    for vnode in vfront:
        new_node = Node(None, label=str(i))
        vnode.add_edge(Edge(), new_node)
        new_vfront.append(new_node)

    for hnode in hfront:
        new_node = Node(None, label=str(i))
        hnode.add_edge(Edge(), new_node)
        new_hfront.append(new_node)

    corner_node = Node(None, label=str(i))
    new_vfront.append(corner_node)
    new_hfront.append(corner_node)

    for node1, node2 in itertools.pairwise(new_vfront):
        node1.add_edge(Edge(), node2)

    for node1, node2 in itertools.pairwise(new_hfront):
        node1.add_edge(Edge(), node2)

    vfront = new_vfront
    hfront = new_hfront

print(graph)
