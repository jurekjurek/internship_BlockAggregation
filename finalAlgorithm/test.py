import numpy as np



def is_swappable(a, b):
    commutationMatrix = np.zeros((4,4), dtype=bool)\

    for i in range(4): 
        for j in range(4): 
            if i == j: 
                commutationMatrix[i, j] = True

            if i == j-1 or j == i-1: 
                commutationMatrix[i,j] = False
            else: 
                commutationMatrix[i, j] = True

    print(commutationMatrix)

    if commutationMatrix[a-1, b-1] == True: 
        result = True
    else: 
        result = False

    return True

def generate_permutations(arr, start=0):
    if start == len(arr):
        yield list(arr)  # A permutation is complete, yield it.
    else:
        for i in range(start, len(arr)):
            if start == i or is_swappable(arr[start], arr[i]):
                arr[start], arr[i] = arr[i], arr[start]  # Swap neighbors.
                yield from generate_permutations(arr, start + 1)  # Recurse on the next element.
                arr[start], arr[i] = arr[i], arr[start]  # Restore the array.

# Example usage:
original_list = [1, 2, 3, 4]
permutations = list(generate_permutations(original_list))

for perm in permutations:
    print(perm)
