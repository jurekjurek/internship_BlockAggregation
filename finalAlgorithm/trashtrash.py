import numpy as np


def is_swap_allowed(a, b):
    # Define your metric or condition for allowing a swap here.
    # Return True if the swap is allowed, False otherwise.
    # Example condition: return a < b

    commutationMatrix = np.zeros((4,4), dtype=bool)\
    
    commutationMatrix[0,0] = True 
    commutationMatrix[1,1] = True 
    commutationMatrix[2,2] = True 
    commutationMatrix[3,3] = True 

    commutationMatrix[0,1] = True 
    commutationMatrix[1,0] = True
    commutationMatrix[0,2] = False 
    commutationMatrix[2,0] = False
    commutationMatrix[1,2] = True 
    commutationMatrix[2,1] = True

    for i in range(4): 
        for j in range(4): 
            if i == j: 
                commutationMatrix[i, j] = True

            if i == j-1: 
                commutationMatrix[i,j] = False
            else: 
                commutationMatrix[i, j] = True

    print(commutationMatrix)

    if commutationMatrix[a-1, b-1] == True: 
        result = True
    else: 
        result = False

    return result

def generate_permutations(arr, start=0):
    if start == len(arr) - 1:
        yield arr.copy()  # Return a copy of the current permutation
    else:
        for i in range(start, len(arr)):
            # Check if the swap is allowed based on your metric
            if is_swap_allowed(arr[start], arr[i]):
                # Swap elements
                arr[start], arr[i] = arr[i], arr[start]
                # Recursively generate permutations for the rest of the list
                yield from generate_permutations(arr, start + 1)
                # Swap back to the original order to explore other permutations
                arr[start], arr[i] = arr[i], arr[start]

# Example usage
input_list = [1, 2, 3, 4]
permutations = list(generate_permutations(input_list))
print(permutations)