'''
to check if two gates commute, we do the following. 

We get the random circuit by quiskit. This is a circuit that does a random manipulation of two random qubits with one another. 
Now, for each gate, we look at the corresponding part in the circuit and calculate the matrix of this *part* of the circuit. 
Then, to check if these two commute, we take the two matrices A and B - corresponding to the two Gates and check if 

A * B = B * A

if so, they commute. 

Then, we have to make the circuit compatible with the format of *numbers* that our block aggregation (and the optimization) works with. 
So, we have to reduce the propery of commuting gates with numbers (the numbers of the gates) and the numbers of the qubits that these gates hold.


to do: 
gates *only* operate on two qubits!!

'''
from itertools import permutations

from qiskit import *
# from qiskit.circuit.random import random_circuit
from AlteredRandomCircuitSourceCode import randomCircuitTwoQubits
from GetMatrixFromCircuit import calculate_circuit_matrix
from qiskit import QuantumCircuit
from qiskit import Aer
from qiskit.extensions import UnitaryGate
import matplotlib.pyplot as plt
import numpy as np

import copy


# necessary for later
def CheckCommutation(matrixOne, matrixTwo): 

    resultOne = np.matmul(matrixOne, matrixTwo)

    resultTwo = np.matmul(matrixTwo, matrixOne)

    # if resultOne == resultTwo: 
    if np.array_equal(resultOne, resultTwo):
        return True 
    else: 
        return False 



def CountGates(qc: QuantumCircuit): 
    '''
    This function counts the gates in a circuit
    '''
    gateCount = {qubit: 0 for qubit in qc.qubits}
    for gate in qc.data: 
        for qubit in gate.qubits: 
            gateCount[qubit] += 1 
    
    return gateCount



def RemoveUnusedQubits(qc: QuantumCircuit):
    '''
    This function removes qubits from a circuit that are unused. 
    We will need this function when investigating the commutation behaviour between gates
    '''
    gateCount = CountGates(qc)
    for qubit, count in gateCount.items():
        if count == 0: 
            qc.qubits.remove(qubit)
    
    return qc



def CreateRandomCircuit(nQubits, nGates, maxNumberOperations, display):
    '''
    returns: 
        - List of numbered gates with correspoding qubits that are operated upon
        - List of matrices corresponding to these gates 

    '''

    # first, create one circuit with only one gate 
    circuitToBeAltered, involvedQubits = randomCircuitTwoQubits(nQubits, 1, maxNumberOperations, measure=False)

    if nGates < 1:
        print('Error, number of gates smaller than one.')
        return 

    print(circuitToBeAltered)

    gatesList = [[0, involvedQubits]]


    # this numpy array will contain matrices, these matrices will be of size 8x8. 
    # They correspond to the commutation
    # listOfMatrices = np.zeros(nGates, dtype=object)

    # backend = Aer.get_backend('unitary_simulator')
    # job = execute(circuitToBeAltered, backend)
    # result = job.result()

    # listOfMatrices[0] = result.get_unitary(circuitToBeAltered, decimals = 3)


    listOfTempCircuits = [circuitToBeAltered]

    # iterate over gates that we are going to create
    for iGate in range(nGates-1):

        # if we reached the last gate, we do want to measure 
        if iGate == nGates -2:
            # was true before, but problems with matrix representation 
            tempCirc, involvedQubits = randomCircuitTwoQubits(nQubits, 1, maxNumberOperations, measure=False)
        else:
            tempCirc, involvedQubits = randomCircuitTwoQubits(nQubits, 1, maxNumberOperations, measure=False)


        # collect the tempcircuits to reason about commutation behaviour later 
        listOfTempCircuits.append(tempCirc)

        # tempCirc.draw(output = 'mpl')
        # plt.title('TEMPCIRC')
        # plt.show()

        # backend = Aer.get_backend('unitary_simulator')
        # job = execute(tempCirc, backend, shots=8192)
        # result = job.result()

        # tempMatrix = result.get_unitary(tempCirc,3)

        # print(tempCirc)

        # backend = Aer.get_backend('unitary_simulator')
        # job = execute(tempCirc, backend)
        # result = job.result()
        # # print(result.get_unitary(tempCirc, decimals=3))

        # listOfMatrices[iGate+1] = result.get_unitary(tempCirc, decimals = 3)



        # At this point, we created the temporary circuit. Now we want to check if it commutes with the other circuits that we have seen. 




        gatesList.append([iGate+1, involvedQubits])
        
        # add barrier to the main circuit, then add the temporary circuit
        # circuitToBeAltered.barrier()
        circuitToBeAltered = circuitToBeAltered.compose(tempCirc)

        '''
        for every new part of the circuit, evaluate the matrix and store it in a list of matrices. 
        Then, to check what gate acts on which qubits, look at the rows in the matrices where the matrix is not equal to the unitary matrix. 
        These are the qubits that are being acted on. 
        '''
    

    if display: 
        circuitToBeAltered.draw(output='mpl')

        plt.show()

        print(circuitToBeAltered)

    # I guess here is a good place to define the commuation matrix
    commutationMatrix = np.zeros((nGates, nGates))

    for gateNo in range(len(gatesList)): 

        gate = gatesList[gateNo]
        q1, q2 = gate[1]

        for otherGateNo in range(len(gatesList)): 

            # gate always commutes with itself
            if gateNo >= otherGateNo: 
                continue

            otherGate = gatesList[otherGateNo]
            otherQ1, otherQ2 = otherGate[1]

            # create two circuits based on the gates circuit representation (stored in tempcircuitList) 
            # and see if the corresponding matrices commute
            circuit1 = listOfTempCircuits[gateNo]
            circuit2 = listOfTempCircuits[otherGateNo]

            # the circuits now consist of two qubits each
            circuit1 = RemoveUnusedQubits(circuit1)
            circuit2 = RemoveUnusedQubits(circuit2)

            testCircuit = QuantumCircuit(3)

            # create a circuit with three qubits with both of the gates 
            if q1 == otherQ1: 
                circuit1 = testCircuit.compose(circuit1, [0, 2])
                circuit2 = testCircuit.compose(circuit2, [0, 1])
                # combinedCircuit = circuit1.compose(circuit2, [0, 1])
            
            elif q2 == otherQ2: 
                circuit1 = testCircuit.compose(circuit1, [0, 2])
                circuit2 = testCircuit.compose(circuit2, [1, 2])
                # combinedCircuit = circuit1.compose(circuit2, [1, 2])

            elif q1 == otherQ2: 
                circuit1 = testCircuit.compose(circuit1, [1, 2])
                circuit2 = testCircuit.compose(circuit2, [0, 1])
                # combinedCircuit = circuit1.compose(circuit2, [0, 1])

            elif q2 == otherQ1: 
                circuit1 = testCircuit.compose(circuit1, [0, 1])
                circuit2 = testCircuit.compose(circuit2, [1, 2])
                # combinedCircuit = circuit1.compose(circuit2, [1, 2])

            # if the two circuits do not share any qubits, just continue. They will certainly commute 
            # BUT: we do not set the indices of the commuationmatrix to one here. The commutationmatrix should tell us the commutation behaviour between 
            # gates that are not obvious - such that share qubits!!
            else: 
                # commutationMatrix[gateNo, otherGateNo] = 1
                # commutationMatrix[otherGateNo, gateNo] = 1
                continue

            
            # get matrix representation of circuit 1
            backend = Aer.get_backend('unitary_simulator')
            job = execute(circuit1, backend)
            result = job.result()

            circuit1Matrix = result.get_unitary(circuit1, decimals = 3)

            # get matrix representation of circuit 2
            backend = Aer.get_backend('unitary_simulator')
            job = execute(circuit2, backend)
            result = job.result()

            circuit2Matrix = result.get_unitary(circuit2, decimals = 3)


            if CheckCommutation(circuit1Matrix, circuit2Matrix): 

                print('We actually improved the method for gates', gate, ' and ', otherGate)

                commutationMatrix[gateNo, otherGateNo] = 1

                # symmetric
                commutationMatrix[otherGateNo, gateNo] = 1








    return gatesList, commutationMatrix

gatesList, commutationMatrix = CreateRandomCircuit(20, 40, 2, display = False)



def ShowCommutationMatrix(commutationMatrix):
    '''
    plot the commutationmatrix
    '''
    import seaborn as sns

    # Create a heatmap using Seaborn

    a = sns.heatmap(commutationMatrix, annot=False, cmap='binary')

    testArray = np.zeros((40, 40))

    for i in range(40): 
        for j in range(40):
            if i == j+1 or j == i+1: 
                testArray[i, j] = 1

    # Add labels and title
    plt.xlabel('Gate no.')
    plt.ylabel('Gate no.')
    plt.title('Commutation Matrix')

    b = sns.heatmap(testArray, annot=False, cmap='binary', alpha = 0.2, cbar=False)
    # b.color
    # Show the plot

    plt.show()





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


def BFS(listOfPossibleArrangements, commutationMatrix): 
    '''
    this function receives a list of gates in a certain order, and a commutation matrix 
    BAsed on this commutationmatrix, it assembles all different combinations of gates in the list that are possible 
    '''

    tempGatesList = listOfPossibleArrangements[-1]

    print(tempGatesList)

    gatesList = [gate[0] for gate in tempGatesList]

    # BFS works like this: We iterate over the swaps between direct neighbours. If they swap, we append a list of the array with swapped values to 
    # allAllowedArrangements. 
    # we then have a list of all possible arrangements. For each step in the tree, we check if 

    # ListOfPossibleArrangements = [gatesList]

    # we want to know which matrices commute, so we get all of the indices, corresponding to gates - where matrices commute 
    commutingGates = np.where(commutationMatrix)

    print('Commuting Gates:', commutingGates)

    if not np.any(commutationMatrix): 
        return listOfPossibleArrangements

    for i in range(len(gatesList)-1):

        tempGate1 = gatesList[i]
        tempGate2 = gatesList[i+1]

        # print('DEBUGDEBUG')
        # print(np.shape(commutingGates), commutingGates)
        # tempArray = np.array([tempGate1, tempGate2])

        # isPresent = any(np.array_equal(tempArray, arr) for arr in commutingGates)

        # print('isitpresente????',isPresent)

        for j in range(len(commutingGates[0])): 
            # print(commutingGates[0])
            if tempGate1 == commutingGates[0][j] and tempGate2 == commutingGates[1][j]: 
                print('TESTEST, IS THIS EXECUTED???')
                tempList = copy.deepcopy(tempGatesList)

                tempList[tempGate1], tempList[tempGate2] = tempList[tempGate2], tempList[tempGate1]

                if tempList in listOfPossibleArrangements: 
                    continue

                listOfPossibleArrangements.append(tempList)

                listOfPossibleArrangements = BFS(listOfPossibleArrangements, commutationMatrix)

        # if [tempGate1, tempGate1] in commutingGates: 

        #     tempList = copy.deepcopy(gatesList)

        #     tempList[tempGate1], tempList[tempGate2] = tempList[tempGate2], tempList[tempGate1]

        #     if tempList in ListOfPossibleArrangements: 
        #         continue

        #     ListOfPossibleArrangements.append(tempList)

        #     ListOfPossibleArrangements = BFS(ListOfPossibleArrangements, commutationMatrix)

    return listOfPossibleArrangements



newGatesList = []
newGatesList = gatesList

# for gateNo in range(len(gatesList)): 
#     newGatesList.append(gatesList[gateNo][0])

# BFS works like this: We iterate over the swaps between direct neighbours. If they swap, we append a list of the array with swapped values to 
# allAllowedArrangements. 
# we then have a list of all possible arrangements. For each step in the tree, we check if 

ListOfPossibleArrangements = [newGatesList]


newLOPA = BFS(ListOfPossibleArrangements, commutationMatrix)

# print(commutationMatrix)





print('newloopa', np.shape(newLOPA))
ShowCommutationMatrix(commutationMatrix)
