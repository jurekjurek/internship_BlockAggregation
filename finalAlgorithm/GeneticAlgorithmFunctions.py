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

    population = []

    for i in range(populationSize): 
        tempProcessingBlockArrangement = blockProcessCircuit(circuitOfQubits, nQ, storageZoneShape, qMax, mMax)
        # print(np.shape(tempProcessingBlockArrangement))
        population.append(tempProcessingBlockArrangement)

    return population

def TournamentSelection(fitnessList, tournamentProbability, tournamentSize):
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

    lenIndividuals = len(individualOne)

    # we will start by exchanging processing blocks between two individuals and see how this goes 
    randomLayer = random.randint(0,lenIndividuals)

    individualTwoNew = individualTwo[0:randomLayer] + individualOne[randomLayer:lenIndividuals]
    individualOneNew = individualOne[0:randomLayer] + individualTwo[randomLayer:lenIndividuals]



    return individualOneNew, individualTwoNew


def Mutation(individual, mutationProbability, alpha): 
    '''
    For an entire population of individuals, this function iterates over all the individuals and manipulates each one of these with the probability mutationProbability
    With each the propability mutationProbability, the following operations are done: 
        1. Two qubits between idle zones are swapped
        2. Two qubits in idle zones are swapped 
        3. Whole processing Zones are swapped 
        4. Qubits within processing zones are swapped

    '''
    
    # 
    # if we really want to explore instead of exploiting in the beginning, we can swap whole processing blocks! In the beginning, this does make sense 
    # when we are comparing different solutions to each other. But once a significant amount of ooptimisation has happened, this loses its meaning since 
    # an optimal placement of one processing block relies on its position with respect to its left and right neighbours 
    # 

    randomProbabilityBlocks = random.random()
    if alpha > 0.5 and randomProbabilityBlocks < mutationProbability: 

        # pick two *blocks* at random 
        randomLayer1 = random.randint(0,len(individual))

        randomLayer2 = random.randint(0,len(individual))

        # and make sure that they are not the same
        while randomLayer1 == randomLayer2: 
            randomLayer2 = random.randint(0,len(individual))

        # this step is very simple, just switch the entire processing blocks in the individual with each other 
        tempBlock = individual[randomLayer2]
        individual[randomLayer2] = individual[randomLayer1]
        individual[randomLayer1] = tempBlock

        # this is it - we don't have to adjust pointers or qubits themselves






    randomProbability = random.random()

    # swap qubits in processing zone
    if randomProbability < mutationProbability * 1/4:

        randomLayer = random.randint(0,len(individual))

        # list of qubits in processing zones
        processingZoneQubits = individual[randomLayer][0]

        randomProcessingZoneIndex = random.randint(0, len(processingZoneQubits))

        # picks two qubits from the random processing zone to swap 
        # qubitsToBeSwapped = random.sample(randomProcessingZone, 2)

        # qubit1 = qubitsToBeSwapped[0]
        # qubit2 = qubitsToBeSwapped[1]

        # pick two random positions in the processing zone, correspoding to two qubits 
        randomIndexQubit1 = random.randint(0, len(processingZoneQubits[randomProcessingZoneIndex]))
        randomIndexQubit2 = random.randint(0, len(processingZoneQubits[randomProcessingZoneIndex]))

        # have to be different from each other 
        while randomIndexQubit2 == randomIndexQubit1: 
            randomIndexQubit2 = random.randint(0, len(processingZoneQubits[randomProcessingZoneIndex]))

        # Swaps qubit one and two in layer randomLayer
        # we do not need to provide the information about the natrue of the zone, that is stored in the individual itself 
        individual  = SwapQubits(individual, randomLayer, 'processing', randomProcessingZoneIndex, randomProcessingZoneIndex, randomIndexQubit1, randomIndexQubit1)




    # swap idle qubits with each other. Between storage zones as well as inside of individual storage zones 
    elif randomProbability < mutationProbability * 0.75:

        # again, pick a random layer 
        randomLayer = random.randint(0,len(individual))

        # list of qubits in this layer that are inside storage zones 
        storageZoneQubits = individual[randomLayer][2]

        randomStorageZoneIndex1 = random.randint(0, len(storageZoneQubits))
        randomStorageZoneIndex2 = random.randint(0, len(storageZoneQubits))

        # pick two of these qubits in storage zones 
        randomIndexQubit1 = random.randint(0, len(storageZoneQubits[randomStorageZoneIndex1]))
        randomIndexQubit2 = random.randint(0, len(storageZoneQubits[randomStorageZoneIndex2]))

        while randomIndexQubit2 == randomIndexQubit1: 
            randomIndexQubit2 = random.randint(0, len(storageZoneQubits[randomStorageZoneIndex2]))

        # swap these two qubits that are stored in storage zones 
        individual = SwapQubits(individual, randomLayer, 'storage', randomStorageZoneIndex1, randomStorageZoneIndex2, randomIndexQubit1, randomIndexQubit2)

        return 



    # randomly swap whole processing zones with each other 
    elif randomProbability < mutationProbability: 

        # start again by picking random layer 
        randomLayer = random.randint(0,len(individual))

        # qubits in processing zone in this layer 
        processingZoneQubits = individual[randomLayer][0]

        # now, pick two processing zones at random
        randomProcessingZoneIndex1 = random.randint(0, len(processingZoneQubits))
        randomProcessingZoneIndex2 = random.randint(0, len(processingZoneQubits))

        # this time, the processing zones cannot be the same 
        while randomProcessingZoneIndex1 == randomProcessingZoneIndex2: 
            randomProcessingZoneIndex2 = random.randint(0, len(processingZoneQubits))
            
        individual = SwapProcessingZones(individual, randomLayer, randomProcessingZoneIndex1, randomProcessingZoneIndex2)

        return 


    else: 

        # I don't know if that makes sense! 
        return 


def SwapQubits(individual, layer, zoneNature, zoneNumberQubit1, zoneNumberQubit2, indexQubit1, indexQubit2):
    '''
    This function returns an individual with the corresponding qubits exchanged 
    zoneNature is a string, either 'processing' or 'storage' 
    '''

    blockOfInterest = individual[layer]

    processingZoneQubits = blockOfInterest[0]

    storageZoneQubits    = blockOfInterest[2]

    if zoneNature == 'processing': 

        # [zoneNumberQubit1] = [zoneNumberQubit2] for processingzone qubits, because we do not swap in betweeen zones 

        tempValue                                             = processingZoneQubits[zoneNumberQubit1][indexQubit1]
        processingZoneQubits[zoneNumberQubit1][indexQubit1]   = processingZoneQubits[zoneNumberQubit1][indexQubit2]
        processingZoneQubits[zoneNumberQubit1][indexQubit2]   = tempValue

        # adjust pointerQuadruple 
        # we only have to adjust the position *in* the zone;
        # the nature of the zone, the nature of the qubit as well as the processing zone number stay the same 
        pointerQuadruple = blockOfInterest[3]

        qubit1 = processingZoneQubits[indexQubit1]
        qubit2 = processingZoneQubits[indexQubit2]

        positionInZoneQubit1 = pointerQuadruple[2][qubit1]
        positionInZoneQubit2 = pointerQuadruple[2][qubit2]

        pointerQuadruple[2][qubit2] = positionInZoneQubit2 
        pointerQuadruple[2][qubit1] = positionInZoneQubit1


    elif zoneNature == 'storage':
        tempValue                                           = storageZoneQubits[zoneNumberQubit1][indexQubit1]
        storageZoneQubits[zoneNumberQubit1][indexQubit1]    = storageZoneQubits[zoneNumberQubit2][indexQubit2]
        storageZoneQubits[zoneNumberQubit2][indexQubit2]    = tempValue

        # adjust pointerQuadruple 
        # we only have to adjust the position *in* the zone;
        # the nature of the zone, the nature of the qubit as well as the processing zone number stay the same 
        pointerQuadruple = blockOfInterest[3]

        qubit1 = processingZoneQubits[indexQubit1]
        qubit2 = processingZoneQubits[indexQubit2]

        positionInZoneQubit1 = pointerQuadruple[2][qubit1]
        positionInZoneQubit2 = pointerQuadruple[2][qubit2]

        pointerQuadruple[2][qubit2] = positionInZoneQubit2 
        pointerQuadruple[2][qubit1] = positionInZoneQubit1

        # for storage zone qubits, we ggf. also have to switch the storage zone number! 
        pointerQuadruple[1][qubit1] = zoneNumberQubit2
        pointerQuadruple[1][qubit2] = zoneNumberQubit1




    else: 
        print('Error. ZoneNature in SwapQubits is not assigned correctly.')
        return


    # assign the processingzone and storagezone qubits to the individual again 
    individual[layer][0] = processingZoneQubits
    individual[layer][2] = storageZoneQubits
        
    # and pointer as well 
    individual[layer][3] = pointerQuadruple


    return individual 
    


def SwapProcessingZones(individual, layer, indexProcessingZone1, indexProcessingZone2):
    '''
    Given: 
        
    this function exchanges *all* qubits in processing Zone number 1 with all qubits in processing zone number 2. 

    Remeber: Here indexProcessingZone1 is equal to the actual nubmer of the processing zone 

    '''

    blockOfInterest = individual[layer]

    processingZoneQubits = blockOfInterest[0]


    # swap all the qubits in the processing zones - amounts to swapping corresponding sublists 

    processingZone1Qubits = processingZoneQubits[indexProcessingZone1]
    processingZone2Qubits = processingZoneQubits[indexProcessingZone2]

    processingZoneQubits[indexProcessingZone1] = processingZone2Qubits
    processingZoneQubits[indexProcessingZone2] = processingZone1Qubits 


    # adjust pointer
    # the positions *within* the processing zones stay the same!
    pointerQuadruple = blockOfInterest[3]
    processingZoneNumbersForQubits = pointerQuadruple[1]


    for iQubit in range(len(processingZoneNumbersForQubits)):
        if processingZoneNumbersForQubits[iQubit] == indexProcessingZone1:
            processingZoneNumbersForQubits[iQubit] = indexProcessingZone2
        elif processingZoneNumbersForQubits[iQubit] == indexProcessingZone2:
            processingZoneNumbersForQubits[iQubit] = indexProcessingZone1

    
    # update individual to return 

    # update qubit list
    individual[layer][0] = processingZoneQubits
    # and processing zone numbers for qubits in pointer 
    individual[layer][3][1] = processingZoneNumbersForQubits



    return individual
