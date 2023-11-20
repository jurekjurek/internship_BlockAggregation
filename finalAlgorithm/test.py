from itertools import permutations
import numpy as np


def is_valid_permutation(permutation, commutation_restrictions, originalList):

    # for the gates in the restriction list, it is forbidden to 

    for gate1, gate2 in commutation_restrictions:
        index1 = permutation.index(gate1)
        index2 = permutation.index(gate2)


        # where are gate 1 and 2 in the original list? 

        originalIndex1 = np.where(originalList == gate1)[0][0]
        originalIndex2 = np.where(originalList == gate2)[0][0]


        if np.sign(originalIndex1 - originalIndex2) != np.sign(index1 - index2): 
            return False 


        # if index1 > index2:
        #     index1, index2 = index2, index1  # Swap indices to ensure index1 < index2
        # if not (index2 - index1 > 1):
        #     return False  # The gates violate commutation restrictions
    return True

def generate_valid_permutations(gates, commutation_restrictions, originalList):
    all_permutations = permutations(gates)

    print(all_permutations)

    valid_permutations = [p for p in all_permutations if is_valid_permutation(p, commutation_restrictions, originalList)]
    return valid_permutations

# Example usage:
gates = ['g1', 'g2', 'g3']
commutation_restrictions = [('g2', 'g3')]

originalList = np.array(gates)

valid_permutations = generate_valid_permutations(gates, commutation_restrictions, originalList)

for i, permutation in enumerate(valid_permutations):
    print(f"Permutation {i + 1}: {permutation}")


arr = np.array([1, 2, 3, 4, 5])

# Specify the element you want to find
element_to_find = 3

# Get the indices where the element occurs
indices = np.where(arr == element_to_find)[0][0]

# Print the indices
print("Index of", element_to_find, ":", indices)
