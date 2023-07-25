import networkx as nx
import matplotlib.pyplot as plt

'''
This programme displays processing blocks of N qubits. 
In each block, the qubits are arranged differently. 
For asthetic reasons, qubit n in a block is connected with a line to qubit n in its neighbouring blocks. 

'''

# Create an empty directed graph
G = nx.MultiDiGraph()

# Add nodes to the graph
layers = [
    ['1', '2', '3'],     # Layer 0
    ['1', '3', '2'],     # Layer 1 (same labels as Layer 0)
    ['3', '2', '1'],     # Layer 2 (same labels as Layer 0)
]


'''
This is a really ugly solution, this has to be improved. 
For now, in order to display nodes that are displayed with the same labels, we add a '*' to the label and upon displaying, we erase it. 
'''
for layer_idx, layer in enumerate(layers):
    modified_layer = [f"{node}{'*' * layer_idx}" for node in layer]  # Modify the node labels
    G.add_nodes_from(modified_layer)
    if layer_idx > 0:
        for node in layers[layer_idx - 1]:
            for neighbour in layer:
                if node == neighbour:  # Compare the original labels, not the modified ones
                    G.add_edge(f"{node}{'*' * (layer_idx - 1)}", f"{neighbour}{'*' * layer_idx}")

# Set the position of the nodes based on their layers
pos = {}
for layer_idx, layer in enumerate(layers):
    for node_idx, node in enumerate(layer):
        pos[f"{node}{'*' * layer_idx}"] = (layer_idx, -node_idx)  # Use modified labels for positioning

# Draw the graph with different colors for each layer
plt.figure(figsize=(8, 6))

# Assign different colors to each layer
# layer_colors = ['skyblue', 'lightgreen', 'lightcoral']

for layer_idx, layer in enumerate(layers):
    modified_layer = [f"{node}{'*' * layer_idx}" for node in layer]  # Modify the node labels for visualization
    labels = {node: node.rstrip('*') for node in modified_layer}  # Remove '*' for node labels display
    nx.draw_networkx_nodes(G, pos, nodelist=modified_layer, 
    # node_color=layer_colors[layer_idx], 
    node_size=1000, label=f'Layer {layer_idx}')
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=12, font_weight='bold')  # Display node labels

nx.draw_networkx_edges(G, pos, arrows=True)

# Uncomment the following line to display a legend
# plt.legend()

plt.axis('off')
plt.show()


