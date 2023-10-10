'''
In this file, I will try to apply a genetic algorithm to the problem of uncluttering a graph. 
The metric that guides the minimization procedure is defined in the function computeTotalCost. 

What we essentially start with is a procedure to randomize the idle qubits in each processing block. 
So we iterate over each of the processing blocks, and if natureStatus = 'i', we collect it in an idle pool. 
We scramble the qubits in this idle pool and then reassign them to their positions before. 

We could also do this in the block aggregation procedure. 
'''

from HelperFunctions import * 
from BlockAggregation import *






'''

We initialized the population and the corresponding fitness for this population
Now for the 
1. mutation and the 
2. crossover and the 
3. tournament selection 
functions 

'''

def InitializePopulation(populationSize, nQ, gates, storageZoneShape, qMax, mMax):
    '''
    The population is merely a list of processing block arrangements
    '''

    circuitOfQubits = random_circuit(nQ, gates)    

    population = np.zeros(populationSize)

    for i in populationSize: 
        population[i] = blockProcessCircuit(circuitOfQubits, nQ, storageZoneShape, qMax, mMax)


def TournamentSelection(fitnessList, tournamentProbability):
    populationSize = len(fitnessList)

    randomIndividualOne = random.randint(0, populationSize-1)    
    randomIndividualTwo = random.randint(0, populationSize-1)

    randomProbability = random.random()

    if randomProbability < tournamentProbability: 
        if fitnessList[randomIndividualOne] > fitnessList[randomIndividualTwo]: 
            return(randomIndividualOne)
        else: 
            return(randomIndividualTwo)

    if randomProbability > tournamentProbability: 
        if fitnessList[randomIndividualOne] > fitnessList[randomIndividualTwo]: 
            return(randomIndividualTwo)
        else: 
            return(randomIndividualOne)






def CrossOver(individualOne, individualTwo): 
    '''
    Given two individuals (processingBlockArrangements), this function performs something corresponding to the genetic crossover of two genes
    Accepts: 
        Two processingBlockLists
    Returns: 
        Two new processingBlockLists
    '''

    return None 


def Mutation(individual, mutationProbability): 
    '''
    For an entire population of individuals, this function iterates over all the individuals and manipulates each one of these with the probability mutationProbability
    With each the propability mutationProbability, the following operations are done: 
        1. Two qubits between idle zones are swapped
        2. Two qubits in idle zones are swapped 
        3. Whole processing Zones are swapped 
        4. Qubits within processing zones are swapped

    '''
    
    randomProcessingQubitSwaps = random.random()

    randomProbability = random.random()

    # swap qubits in processing zone
    if randomProbability < mutationProbability * 1/4:

        randomLayer = random.randint(0,len(individual))

        # list of qubits in processing zones
        processingZoneQubits = individual[randomLayer][1]

        randomProcessingZone = random.randint(0, len(processingZoneQubits))

        # picks two qubits from the random processing zone to swap 
        qubitsToBeSwapped = random.sample(randomProcessingZone, 2)

        qubit1 = qubitsToBeSwapped[0]
        qubit2 = qubitsToBeSwapped[1]

        # Swaps qubit one and two in layer randomLayer
        # we do not need to provide the information about the natrue of the zone, that is stored in the individual itself 
        SwapQubits(individual, layer, qubit1, qubit2)

    # swap idle qubits with each other. Between storage zones as well as inside of individual storage zones 
    elif randomProbability < mutationProbability * 0.75:

        return 

    # randomly swap whole processing zones with each other 
    elif randomProbability < mutationProbability: 

        return 

    # swap the positions of processing *Blocks*!!
    else: 

        # I don't know if that makes sense! 
        return 

    return None 


def SwapQubits(individual, layer, qubit1, qubit2):
    '''
    kann diese function optimieren indem ich processing zone number auch mit als argument gebe 
    '''

    blockOfInterest = individual[layer]

    processingZoneQubits = blockOfInterest[0]
    storageZoneQubits    = blockOfInterest[2]

    for iProcessingZone in len(processingZoneQubits):

        qubitsInThisProcessingZone = processingZoneQubits[iProcessingZone]

        if qubit1 in qubitsInThisProcessingZone:
            indexQubit1 = qubitsInThisProcessingZone.index(qubit1)
            indexQubit2 = qubitsInThisProcessingZone.index(qubit2)


            # swap qubits one and two 
            tempValue = qubitsInThisProcessingZone[indexQubit1]
            qubitsInThisProcessingZone[indexQubit1] = qubitsInThisProcessingZone[indexQubit2]
            qubitsInThisProcessingZone[indexQubit2] = tempValue


            # and adjust cList accordingly 
            # ...

            break 


    if qubit1 in storageZoneQubits: 
        indexQubit1 = storageZoneQubits.index(qubit1)
        indexQubit2 = storageZoneQubits.index(qubit2)


        # swap qubits one and two 
        tempValue = storageZoneQubits[indexQubit1]
        storageZoneQubits[indexQubit1] = storageZoneQubits[indexQubit2]
        storageZoneQubits[indexQubit2] = tempValue


    # adjust cList 


    # update individual 


    return individual 
    



def MainGeneticAlgorithm(numberOfGenerations, numberOfIndividuals): 
    
    # initialize population, evaluate cost 
    population = []
    fitnessList = []
    for individual in range(numberOfIndividuals): 

            temporaryProcessingBlockArrangement = blockProcessCircuit(circuitOfQubits, NQ, FSIZES, QMAX, MMAX)

            population.append(temporaryProcessingBlockArrangement)

            


    for generation in numberOfGenerations: 
        
        for individual in range(numberOfIndividuals): 
            # store the corresponding fitnessvalue in a fitnesslist 
            temporaryProcessingBlockArrangement = population[individual]
            temporaryCost = computeTotalCost(computeArrangements(temporaryProcessingBlockArrangement, FSIZES, QMAX), NQ)

            fitnessList.append(1/ temporaryCost)



        
