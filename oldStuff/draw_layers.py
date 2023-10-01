import itertools
import matplotlib.pyplot as plt
import networkx as nx

subset_sizes = [5, 5, 5, 5]
subset_color = [
    "gold",
    "violet",
    "violet",
    "violet",
    "violet",
    "limegreen",
    "limegreen",
    "darkorange",
]


S_set = [[1, 2, 4, 6, 8], [2, 1, 4, 8, 6], [6, 8, 4, 2, 1], [4, 2, 1, 6, 8]]

S_set_labels = {n for i in S_set for n in i}


def multilayered_graph(*subset_sizes):
    extents = nx.utils.pairwise(itertools.accumulate((0,) + subset_sizes))
    layers = [range(start, end) for start, end in extents]

    print('layers:', layers)

    G = nx.Graph()

    # for layer_idx, layer in enumerate(layers):
    #     G.add_nodes_from(layer)
    #     if layer_idx > 0:
    #         for node in layers[layer_idx - 1]:
    #             for neighbour in layer:
    #                 if node == neighbour: 
    #                     G.add_edge(node, neighbour)

    # return G

    for i, layer in enumerate(layers):
        G.add_nodes_from(layer, layer=i)
    for layer1, layer2 in nx.utils.pairwise(layers):
        G.add_edges_from(itertools.product(layer1, layer2))
    return G




G = multilayered_graph(*subset_sizes)
color = [subset_color[data["layer"]] for v, data in G.nodes(data=True)]
pos = nx.multipartite_layout(G, subset_key="layer")

# Extract the node labels (node IDs) and create a dictionary for labels
labels = {node: node % 5 + 1 for node in G.nodes()}

print(labels)
plt.figure(figsize=(8, 8))
nx.draw(G, pos, node_color=color, with_labels=False)
nx.draw_networkx_labels(G, pos, S_set_labels, font_size=10, font_color="black", verticalalignment="center")
plt.axis("equal")
plt.show()






