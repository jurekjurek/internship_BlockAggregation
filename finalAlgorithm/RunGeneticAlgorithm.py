from GeneticAlgorithmFunctions import *
from AlternatingOptimization import * 

'''
This file is responsible for running a Genetic algorithm to unclutter a graph. 
'''

# global variables for GA
NUMBEROFGENERATIONS = 10000
POPULATIONSIZE = 50

CROSSOVERPROB = 0.5
MUTATIONPROB = 0.2

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

print('Populationsize:')
print(np.shape(population))

for iGeneration in range(NUMBEROFGENERATIONS): 

    # evaluate individuals and keep a list 
    fitnessList = np.zeros(POPULATIONSIZE)

    maximumFitness = 0 

    # evaluate individuals 
    for jIndividual in range(POPULATIONSIZE):

        tempBrocessingBlockArrangement = population[jIndividual]

        costForThisIndividual = computeTotalCost(computeArrangements(tempBrocessingBlockArrangement, FSIZES, MMAX), NQ)

        fitnessList[jIndividual] = costForThisIndividual
        if fitnessList[jIndividual] > maximumFitness: 
            maximumFitness = fitnessList[jIndividual]
            bestIndividual = jIndividual 


    # proceed with evolution
    tempPopulation = population

    # print(fitnessList)

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

    # exit()
    if iGeneration %100 == 0: 
        print('Best individual: ')
        print(computeTotalCost(computeArrangements(population[bestIndividual], FSIZES, MMAX), NQ))


