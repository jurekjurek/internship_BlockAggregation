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









'''
trash for when swapqubits was more general 

'''
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