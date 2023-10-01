from GeneticAlgorithmFunctions import *
from AlternatingOptimization import * 

# global variables for GA
NUMBEROFGENERATIONS = 10
POPULATIONSIZE = 10

CROSSOVERPROB = 0.2
MUTATIONPROB = 0.04

TOURNAMENTPROBAB = 0.75

# global variables for Block aggregation
NQ = 20
GATES = 40
MMAX = 2
QMAX = 4
FSIZES = [4,4,4]

# initiate circuit
circuitOfQubits = random_circuit(NQ, GATES)


# initialize population which is a list of aggregated processing blocks 
population = InitializePopulation(POPULATIONSIZE, NQ, GATES, FSIZES, QMAX, MMAX)


for generation in range(NUMBEROFGENERATIONS): 

    # evaluate individuals and keep a list 
    fitnessList = np.zeros(POPULATIONSIZE)

    for i in range(POPULATIONSIZE):
        fitnessList[i] = computeTotalCost(population[i], NQ)
