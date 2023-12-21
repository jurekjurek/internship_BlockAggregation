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







'''
from RandomCircuitQiskit.py
'''


def GetCommutationMatrix(listOfGateMatrices): 
    '''
    given a list of the matrices corresponding to the individual gates in the circuit, this funciton creates a symmetric matrix 
    indicating by its i,j-th element if the i-th and j-th matrix in listOfGateMatrices commute
    '''
    numberOfGates = len(listOfGateMatrices)
    commutationMatrix = np.zeros((numberOfGates, numberOfGates))

    for iGate in range(numberOfGates): 
        for jGate in range(numberOfGates): 

            if iGate == jGate: 
                commutationMatrix[iGate, jGate] = 1
                continue

            gate1Matrix = listOfGateMatrices[iGate]
            gate2Matrix = listOfGateMatrices[jGate]

            if CheckCommutation(gate1Matrix, gate2Matrix): 
                commutationMatrix[iGate, jGate] = 1
                print('Gate ', iGate, ' and ', jGate, ' commute.')
            else: 
                commutationMatrix[iGate, jGate] = 0

    return commutationMatrix


# commutationMatrix = GetCommutationMatrix(listOfGateMatrices)

def IsValidPermutation(permutation, commutationMatrix, originalList):
    '''
    originalList is the only constellation of gates that we know to be actually valid 
    '''
    # for the gates in the restriction list, it is forbidden to 


    # for all elements in the matrix that do not commute: 
    for iGate in range(len(commutationMatrix)): 

        for jGate in range(len(commutationMatrix)):

            # if iGate == jGate: 

            #     # remember: we only want non obvious commutation information
            #     return False

            if commutationMatrix[iGate, jGate] == False: 

                
                # in this particular permutation of gates, look where the two gates are that do *not* commute
                index1 = permutation.index(iGate)
                index2 = permutation.index(jGate)


                # where are gate 1 and 2 in the original list? 
                originalIndex1 = np.where(originalList == iGate)[0][0]
                originalIndex2 = np.where(originalList == jGate)[0][0]

                # if the gates have switched the respectives sides to each other, the permutation is not allowed
                if np.sign(originalIndex1 - originalIndex2) != np.sign(index1 - index2): 
                    return False 


            # if the gates do commute, the permutation is allowed
            else: 
                continue

                
    return True





def GetAllValidCircuits(gates, commutationMatrix): 
    '''
    In order to use the Blockaggregation procedure effectively, we have to take into account the differen possible constellations of gates in the circuit
    '''

    # this is a weird step, but for now: 
    # transform [[g1, [q1, q2]], [g2, [q1, q1]], ...] into a simple list [g1,g2, .. ]

    print(gates)

    newGatesList = []

    for gateNo in range(len(gates)): 
        newGatesList.append(gates[gateNo][0])



    all_permutations = permutations(newGatesList)


    valid_permutations = [p for p in all_permutations if IsValidPermutation(p, commutationMatrix, np.array(newGatesList))]


    # store all allowed permutations in a matrix 
    # we're able to get the length of valid_permutations
    AllowedCircuits = np.zeros((len(valid_permutations), len(newGatesList)))


    for i, permutation in enumerate(valid_permutations):
        print(f"Permutation {i + 1}: {permutation}")
        AllowedCircuits[i, :] = permutation

    finalList = []

    # rebuild the original gateslist structure 
    for i in range(len(AllowedCircuits)): 
        currentCircuit = AllowedCircuits[i]

        subList = []

        for j in range(len(currentCircuit)): 
            correspondingQubits = gates[int(currentCircuit[j])][1]
            subList.append([int(currentCircuit[j]), correspondingQubits])

        finalList.append(subList)
        # print('Length of final list: ', len(finalList))

    # print(finalList)


    return AllowedCircuits


# AllowedArrangements = GetAllValidCircuits(gatesList, commutationMatrix)

# print(np.shape(AllowedArrangements))

# print(AllowedArrangements)

# print(commutationMatrix)


'''
After the function GetValidCircuits that gets all of the possible valid circuits, which takes quite a long while, I provide an alternative 


'''


# def GetOnlyOneTimeSwaps(commutationMatrix, gatesList): 

#     # get i and j index - corresponding to gates - in the commutationmatrix where commutationmatrix[i, j] == True
#     # Thus, get the matrices that commute non trivially. 
#     # Then, having sets of two gates [gateOne, gateTwo] iterate over these tuples. If we recognize that two tuples share one gate, add it to the tuple. 
#     # No!
#     # Check if there are neighbouring gates in these tuples, e.g. (1,2) or (4,5)
#     # If we have these, we can update the lists. Then, check if there are tuples like (1,3) or (5,7) among the tuples. If there are, and int((g2 - g1) /2)
#     # was a gate in the former neighbouring ones, we swap the corresponding qubits in the list.
#     # 
#     return None 




# def BreadthFirstSearch(gatesList, commutationMatrix): 
#     '''
    
#     '''
#     print(gatesList)

#     newGatesList = []

#     for gateNo in range(len(gatesList)): 
#         newGatesList.append(gatesList[gateNo][0])

#     # BFS works like this: We iterate over the swaps between direct neighbours. If they swap, we append a list of the array with swapped values to 
#     # allAllowedArrangements. 
#     # we then have a list of all possible arrangements. For each step in the tree, we check if 

#     ListOfPossibleArrangements = [gatesList]

#     # we want to know which matrices commute, so we get all of the indices, corresponding to gates - where matrices commute 
#     commutingGates = np.where(commutationMatrix)


#     for i in range(len(gatesList)-1):

#         tempGate1 = gatesList[i]
#         tempGate2 = gatesList[i+1]

#         if [tempGate1, tempGate1] in commutingGates: 

#             tempList = copy.deepcopy(gatesList)

#             tempList[tempGate1], tempList[tempGate2] = tempList[tempGate2], tempList[tempGate1]

#             if tempList in ListOfPossibleArrangements: 
#                 continue

#             ListOfPossibleArrangements.append(tempList)

#             ListOfPossibleArrangements = BreadthFirstSearch(ListOfPossibleArrangements, commutationMatrix)

#     return ListOfPossibleArrangements



    # for i in range(len(commutingGates)):
    #     currentGates = commutingGates[i]

    #     tempGate1 = currentGates[0]
    #     tempGate2 = currentGates[1]

    #     if np.abs(tempGate1 - tempGate2) == 1: 
            # tempList = copy.deepcopy(gatesList)

            # tempList[tempGate1], tempList[tempGate2] = tempList[tempGate2], tempList[tempGate1]


            # ListOfPossibleArrangements.append(tempList)


# BreadthFirstSearch(gatesList, commutationMatrix)



'''
explanation in blockaggregation:

    If a qubit in one particular gate has been encountered already before, it is part of another pointer set. 
    *BUT* if the gate of this qubit commutes with the other gate that acts on the same qubit in the next step, we can *move* the qubit from the first 
    aggregated sublist to the recent one. 

    ///////////////////////////////
    Here is an EXAMPLE:

    Gate 1: Qubits 9,1 
    Gate 2: Qubits 1,2
    Gate 3: Qubits 3,6
    Gate 4: Qubits 5,7
    Gate 5: Qubits 9,6

    the first step in the algorithm will create S = [[9,1,2], [0], [3], [4], [5], [6], [7], [8]] if we have 10 qubits in total 

    where the first two gates have been taken care of. The next steps are: 

    S = [[9,1,2], [3,6], [5,7], [0], [4], [8]]

    So far, so good. We have not encountered any difficulties with commutation yet. Now, however, we are confronted with the gate 
    Gate 5: Qubits 9,6

    What the algorithm would do so far, taking into account only the fact if there are equal qubits in two gates when evaluating their commutation: 
    S = [[9,1,2,3,6], [5,7], [0], [4], [8]]

    But, what we could do now, when it happens that gate 3 and gate 5 commute: 
    S = [[9,1,2,6], [5,7], [0], [3], [4], [8]]

    as an intermediate step, which *could* lead to a better gate coverage. 
    The best gate coverage could then correspond to this intermediate step. If not, we would of course have to execute gate 5 now as well which would lead us 
    again to: 
    S = [[9,1,2,6,3], [5,7], [0], [4], [8]]

    //////////////////////////////////////////////////
    
    The new commutation aspect only gives us these intermediate steps that *could* provide better gate coverages. And this is essentially what we want. 

    What we essentially have to do in the algorithm: 
    
    Upon merging to sets, merging qubits together: 
    - check if the gates containing the same qubits commute. If they commute: 
        - merge the qubit possibly to next sublists on the left. 
        - essentially do the algorithm, but start now at the left of the sublist that was skipped due to commutation
        - if in there, there is a gate involved that this gate commutes with, we dont have to skip this sublist, since there are only 2 qubits in each gate. 
        - Create the new aggregated qubit sets, merge the corresponding qubit
        - in the next step, execute the gate of interest (corresponding to the last step in the example above)
        - Carry on
    - if they don't commute -> carry on 
'''