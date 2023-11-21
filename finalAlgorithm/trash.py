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





'''
Was in BlockAggregation to deal with commutation 
'''




# das werde ich nicht mehr brauchen 

# def GetCircuitVariations(circuit, commutationMatrix): 
#     '''
#     circuit is a list with this shape: 
#         [[gate1, [qubit2, qubit2]], [gate2, [qubit1, qubit2]], ..., [gateN, [qubit1, qubit2]]]

#     and commutationmatrix is a symmetric matrix that indicates - for the i,j-th element, if gate i and gate j commute. 

#     '''
#     listOfCircuits = []
#     for iGate in circuit.reverse():
#         qubit1 = iGate[0]
#         qubit2 = iGate[1]


#         circuitToBeAltered = circuit

#         # now, for the other gate that we shall check if iGate commutes with 
#         for jGate in circuit[0:iGate].reverse():

#             # check if qubit1 or qubit2 are part of this gate
#             # if so, we check if they commute. 
#             # if they do commute, 
#             if qubit1 in jGate: 
#                 if commutationMatrix(iGate, jGate): 
#                     circuitToBeAltered[iGate] = jGate
#                     circuitToBeAltered[jGate] = iGate
#                     listOfCircuits.append(circuitToBeAltered)
                
#             if qubit2 in jGate: 
#                 if commutationMatrix(iGate, jGate): 
#                     circuitToBeAltered[iGate] = jGate
#                     circuitToBeAltered[jGate] = iGate
#                     listOfCircuits.append(circuitToBeAltered)

#     return listOfCircuits