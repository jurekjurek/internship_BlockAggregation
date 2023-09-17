import random

my_list = [1, 2, 3, 4, 5]

# Generate a random index within the range of the list
random_index = random.randint(0, len(my_list) - 1)

# Remove the element at the random index
random_element = my_list.pop(random_index)

print("Random element:", random_element)
print("Updated list:", my_list)



