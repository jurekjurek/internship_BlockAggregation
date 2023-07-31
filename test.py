import numpy as np

G = [[] for _ in range(10)]
G_np = np.array(G)


print(np.shape(G_np))
print(G_np)

G_np[4] = 5

print(G_np)