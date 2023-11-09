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



individualOfInterest = population[0]

# print(individualOfInterest)


individualOfInterestNew = Mutation(individualOfInterest, MUTATIONPROB, alpha)

print('Are these two the same???', individualOfInterest == individualOfInterestNew)

visualize_blocks(individualOfInterest, 'Before Mutation')
visualize_blocks(individualOfInterestNew, 'After Mutation')