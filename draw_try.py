import matplotlib.pyplot as plt
import networkx as nx
import itertools 
subset_sizes = [10, 10, 10, 10, 10, 10, 10]

def multilayered_graph(*subset_sizes):
    extents = nx.utils.pairwise(itertools.accumulate((0,) + subset_sizes))
    layers = [range(start, end) for start, end in extents]
    G = nx.Graph()
    for i, layer in enumerate(layers):
        G.add_nodes_from(layer, layer=i)
    for layer1, layer2 in nx.utils.pairwise(layers):
        G.add_edges_from(itertools.product(layer1, layer2))
    return G

G = multilayered_graph(*subset_sizes)

# Define positions for nodes
pos = {}
for i in range(len(subset_sizes)):
    for j in range(subset_sizes[i]):
        pos[j + sum(subset_sizes[:i])] = (i, j)

labels = {}
for i in range(len(subset_sizes)):
    for j in range(subset_sizes[i]):
        labels[j + sum(subset_sizes[:i])] = str(j + 1)

plt.figure(figsize=(8, 8))
nx.draw(G, pos, labels=labels, with_labels=True)
plt.axis("equal")
plt.show()
