from itertools import product

# Your three objects can take values 0 and 1
possible_values = [0, 1]

# Generate all permutations
all_permutations = list(product(possible_values, repeat=3))

# Print the result
for perm in all_permutations:
    print(perm)
