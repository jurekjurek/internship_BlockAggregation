from GeneticAlgorithmFunctions import *
from AlternatingOptimization import * 

'''
This file is responsible for running a Genetic algorithm to unclutter a graph. 
'''

# global variables for GA
NUMBEROFGENERATIONS = 10000
POPULATIONSIZE = 50

CROSSOVERPROB = 0.5
MUTATIONPROB = 1

TOURNAMENTPROB = 0.75
TOURNAMENTSIZE = 2

# global variables for Block aggregation
NQ = 20
GATES = 40
MMAX = 2
QMAX = 4
FSIZES = [4,4,4]

# initiate circuit
circuitOfQubits = random_circuit(NQ, GATES)


# alpha is the variable that somehow controls explorations vs. exploitation 
alpha = 0


# 
# INITIALIZE POPULATION - a list of aggregated processing blocks 
# 
population = InitializePopulation(POPULATIONSIZE, NQ, GATES, FSIZES, QMAX, MMAX)



individual = population[0]

# print(individualOfInterest)


# individualOfInterestNew = Mutation(individualOfInterest, MUTATIONPROB, alpha)


# check die qubit swap funtion!! 

'''

TEST SWAPQUBITS

'''

# randomLayer = random.randint(0,len(individual)-1)

# # list of qubits in this layer that are inside storage zones 
# storageZoneQubits = individual[randomLayer][2]


# # add the -1s because of python. list[len(list)] is not defined. Last element in list is list[len(list)-1]

# randomStorageZoneIndex1 = random.randint(0, len(storageZoneQubits)-1)
# randomStorageZoneIndex2 = random.randint(0, len(storageZoneQubits)-1)

# # pick two of these qubits in storage zones 
# randomIndexQubit1 = random.randint(0, len(storageZoneQubits[randomStorageZoneIndex1])-1)
# randomIndexQubit2 = random.randint(0, len(storageZoneQubits[randomStorageZoneIndex2])-1)

# # qubit1 = 

# while randomIndexQubit2 == randomIndexQubit1: 
#     randomIndexQubit2 = random.randint(0, len(storageZoneQubits[randomStorageZoneIndex2])-1)

# # swap these two qubits that are stored in storage zones 
# individual = SwapQubits(individual, randomLayer, 'storage', randomStorageZoneIndex1, randomStorageZoneIndex2, randomIndexQubit1, randomIndexQubit2)

# visualize_blocks(individual, 'swapped')
# exit()

# individualOfInterestNew = SwapQubits()


# und dann die Swap processing zone function

'''
Test processingzone swap
'''

# start again by picking random layer 
randomLayer = random.randint(0,len(individual)-1)

# qubits in processing zone in this layer 
processingZoneQubits = individual[randomLayer][0]

# now, pick two processing zones at random
randomProcessingZoneIndex1 = random.randint(0, len(processingZoneQubits)-1)
randomProcessingZoneIndex2 = random.randint(0, len(processingZoneQubits)-1)

# this time, the processing zones cannot be the same 
while randomProcessingZoneIndex1 == randomProcessingZoneIndex2: 
    randomProcessingZoneIndex2 = random.randint(0, len(processingZoneQubits)-1)
    
print('swapping')
print(randomProcessingZoneIndex1, ' and ')
print(randomProcessingZoneIndex2, ' in layer ', randomLayer)

visualize_blocks(individual, 'swapping in layer ' + str(randomLayer))

individualNew = SwapProcessingZones(individual, randomLayer, randomProcessingZoneIndex1, randomProcessingZoneIndex2)

# print('Are these two the same?', individual == individualNew)

visualize_blocks(individualNew, 'after swapping processing zones')


# print('Are these two the same???', individualOfInterest == individualOfInterestNew)

# visualize_blocks(individualOfInterest, 'Before Mutation')
# visualize_blocks(individualOfInterestNew, 'After Mutation')