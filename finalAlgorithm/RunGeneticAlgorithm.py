from GeneticAlgorithmFunctions import *
from AlternatingOptimization import * 

'''
This file is responsible for running a Genetic algorithm to unclutter a graph. 
'''

# global variables for GA
NUMBEROFGENERATIONS = 10
POPULATIONSIZE = 10

CROSSOVERPROB = 0.2
MUTATIONPROB = 0.04

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
alpha = 1


# 
# INITIALIZE POPULATION - a list of aggregated processing blocks 
# 
population = InitializePopulation(POPULATIONSIZE, NQ, GATES, FSIZES, QMAX, MMAX)


for iGeneration in range(NUMBEROFGENERATIONS): 

    # evaluate individuals and keep a list 
    fitnessList = np.zeros(POPULATIONSIZE)

    maximumFitness = 0 

    # evaluate individuals 
    for jIndividual in range(POPULATIONSIZE):
        fitnessList[jIndividual] = computeTotalCost(population[jIndividual], NQ)

        if fitnessList[jIndividual] > maximumFitness: 
            fitnessList[jIndividual] = maximumFitness
            bestIndividual = jIndividual 


    # proceed with evolution
    tempPopulation = population

    # iterate over population, only taking into account every second individual 
    for jIndividual in range(0, POPULATIONSIZE, 2):

        # 
        # TOURNAMENTSELECTION
        # 

        individualOneIndex = TournamentSelection(fitnessList, TOURNAMENTPROB, TOURNAMENTSIZE)
        individualTwoIndex = TournamentSelection(fitnessList, TOURNAMENTPROB, TOURNAMENTSIZE)
        
        randomNumber = random.random()

        # 
        # CROSSOVER
        # 

        individualOne = population[individualOneIndex]
        individualTwo = population[individualTwoIndex]

        if randomNumber < CROSSOVERPROB: 
            
            newIndividualOne, newIndividualTwo = CrossOver(individualOne, individualTwo)

            tempPopulation[jIndividual] = newIndividualOne
            tempPopulation[jIndividual+1] = newIndividualTwo

        else: 
            tempPopulation[jIndividual] = individualOne
            tempPopulation[jIndividual+1] = individualTwo


    # elitism 
    tempPopulation[0] = population[bestIndividual]

    # 
    # MUTATION
    # 
    for jIndividual in range(POPULATIONSIZE):
        tempIndividual = Mutation(tempPopulation[jIndividual], MUTATIONPROB, alpha)
        tempPopulation[jIndividual] = tempIndividual
    

    # update alpha
    alpha *= 0.99

    # update population
    population = tempPopulation



