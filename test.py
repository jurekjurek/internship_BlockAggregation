import networkx as nx
import matplotlib.pyplot as plt
import random

# Create a graph
G = nx.Graph()

# Define the layers and zones
num_layers = 5
num_nodes_per_layer = 10
num_storage_nodes = 3
num_processing_nodes = 4

# Add nodes to the graph with attributes for layers and zones
for layer in range(num_layers):
    # for i in range(num_nodes_per_layer):
    numbers = list(range(10))
    random.shuffle(numbers)
    for i in numbers:
        zone = "storage"
        if i >= num_storage_nodes and i < num_storage_nodes + num_processing_nodes:
            zone = "processing"
        label = i % 10
        G.add_node((layer, i), layer=layer, zone=zone, label=label)

# Connect nodes with the same labels between layers
for layer in range(num_layers - 1):
    for i in range(num_nodes_per_layer):
        current_node = (layer, i)
        next_node = (layer + 1, i)
        G.add_edge(current_node, next_node)

# Create node positions based on layers and zones
pos = {}
for node in G.nodes():
    layer, node_idx = node
    zone = G.nodes[node]['zone']
    x = layer
    if zone == 'storage':
        y = node_idx
    elif zone == 'processing':
        processing_offset = num_storage_nodes / 2
        y = num_storage_nodes + (node_idx % num_processing_nodes) 
    pos[node] = (x, y)

# Draw the graph with labels
node_labels = {node: G.nodes[node]['label'] for node in G.nodes()}
plt.figure(figsize=(10, 8))
nx.draw(G, pos, node_size=400, node_color=['blue' if G.nodes[node]['zone'] == 'storage' else 'red' for node in G.nodes()], labels=node_labels, with_labels=True)
plt.title("Layered Node Visualization with Corrected Zones")
plt.show()
