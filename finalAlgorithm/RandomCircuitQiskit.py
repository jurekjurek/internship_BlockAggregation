'''
to check if two gates commute, we do the following. 

We get the random circuit by quiskit. This is a circuit that does a random manipulation of two random qubits with one another. 
Now, for each gate, we look at the corresponding part in the circuit and calculate the matrix of this *part* of the circuit. 
Then, to check if these two commute, we take the two matrices A and B - corresponding to the two Gates and check if 

A * B = B * A

if so, they commute. 

Then, we have to make the circuit compatible with the format of *numbers* that our block aggregation (and the optimization) works with. 
So, we have to reduce the propery of commuting gates with numbers (the numbers of the gates) and the numbers of the qubits that these gates hold.


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
    this function does three things: 
    1. it creates a random qiskit circuit and
    2. a corresponding gateslist and 
    3. the corresponding commutation matrix 

    '''

    # first, create one circuit with only one gate 
    circuitToBeAltered, involvedQubits = randomCircuitTwoQubits(nQubits, 1, maxNumberOperations, measure=False)

    if nGates < 1:
        print('Error, number of gates smaller than one.')
        return 

    # print(circuitToBeAltered)

    gatesList = [[0, involvedQubits]]


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



        # At this point, we created the temporary circuit. Now we want to check if it commutes with the other circuits that we have seen. 
        gatesList.append([iGate+1, involvedQubits])
        
        # add barrier to the main circuit, then add the temporary circuit
        # circuitToBeAltered.barrier()
        circuitToBeAltered = circuitToBeAltered.compose(tempCirc)
    

    if display: 
        circuitToBeAltered.draw(output='mpl')

        plt.show()

        print(circuitToBeAltered)

    return circuitToBeAltered, gatesList, listOfTempCircuits

    # define commutation matrix. This is a boolean matrix indicating if the i-th and j-th gate commute 
    commutationMatrix = np.zeros((nGates, nGates))

    for gateNo in range(len(gatesList)): 

        gate = gatesList[gateNo]
        q1, q2 = gate[1]

        for otherGateNo in range(len(gatesList)): 

            # gate always commutes with itself
            # we use >= because the matrix is symmetric 
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
            
            elif q2 == otherQ2: 
                circuit1 = testCircuit.compose(circuit1, [0, 2])
                circuit2 = testCircuit.compose(circuit2, [1, 2])

            elif q1 == otherQ2: 
                circuit1 = testCircuit.compose(circuit1, [1, 2])
                circuit2 = testCircuit.compose(circuit2, [0, 1])

            elif q2 == otherQ1: 
                circuit1 = testCircuit.compose(circuit1, [0, 1])
                circuit2 = testCircuit.compose(circuit2, [1, 2])

            # if the two circuits do not share any qubits, just continue. They will certainly commute 
            # BUT: we do not set the indices of the commuationmatrix to one here. The commutationmatrix should tell us the commutation behaviour between 
            # gates that are not obvious - such gates that share qubits!!
            else: 
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

                # DEBUG 
                # print('We actually found a commutation between ', gate, ' and ', otherGate)

                commutationMatrix[gateNo, otherGateNo] = 1

                # symmetric
                commutationMatrix[otherGateNo, gateNo] = 1

    return gatesList, commutationMatrix


# gatesList, commutationMatrix = CreateRandomCircuit(20, 40, 2, display = False)



def ShowCommutationMatrix(commutationMatrix):
    '''
    plot the commutationmatrix
    And also, show the region in which the neighbouring gates are. 
    '''
    import seaborn as sns

    sns.heatmap(commutationMatrix, annot=False, cmap='binary')

    testArray = np.zeros((40, 40))

    for i in range(40): 
        for j in range(40):
            if i == j+1 or j == i+1: 
                testArray[i, j] = 1

    # Add labels and title
    plt.xlabel('Gate no.')
    plt.ylabel('Gate no.')
    plt.title('Commutation Matrix')

    sns.heatmap(testArray, annot=False, cmap='binary', alpha = 0.2, cbar=False)

    plt.show()






def BFS(listOfPossibleArrangements, commutationMatrix): 
    '''
    this function receives a list of gates in a certain order, and a commutation matrix 
    Based on this commutationmatrix, it assembles all different combinations of gates in the list that are possible.
    It works in an iterative manner. 
    '''
    print(len(listOfPossibleArrangements))

    for listNo in range(len(listOfPossibleArrangements)): 

        # print(listNo)

        tempGatesList = listOfPossibleArrangements[listNo]

        # the list of gates of interest if always the one that was appended to the list of possible arrangements last 
        # tempGatesList = listOfPossibleArrangements[-1]

        # define a second list, in which only the gateNumber is stored: [[1, [q1, q2]], [2, [q1, q2]], ...] becomes [1, 2, ...]
        gatesList = [gate[0] for gate in tempGatesList]

        # we want to know which matrices commute, so we get all of the indices, corresponding to gates - where matrices commute 
        # commutingGates is a 2d array, where the j-th index of commutingGates[0] and the j-th index of commutingGates[1] commute
        commutingGates = np.where(commutationMatrix)

        # if there is no gate that commutes with another one non trivially, just return 
        if not np.any(commutationMatrix): 
            return listOfPossibleArrangements

        for i in range(len(gatesList)-1):

            # pick two neighbouring gates. *only* neighbouring gates in the current list are of interest!  
            tempGate1 = gatesList[i]
            tempGate2 = gatesList[i+1]

            # check if they commute by iterating over the commuting gates
            for j in range(len(commutingGates[0])): 

                if tempGate1 == commutingGates[0][j] and tempGate2 == commutingGates[1][j]: 
                    tempList = copy.deepcopy(tempGatesList)

                    # swap the gates
                    tempList[tempGate1], tempList[tempGate2] = tempList[tempGate2], tempList[tempGate1]

                    # if this arrangement is in the list already, continue 
                    if tempList in listOfPossibleArrangements: 
                        print('already in list')
                        continue

                    # if not, we append this newly formed list to the collection of lists 
                    listOfPossibleArrangements.append(tempList)

                    # and we perform the BFS on this new list
                    listOfPossibleArrangements = BFS(listOfPossibleArrangements, commutationMatrix)

    return listOfPossibleArrangements



def BFS_Two(subList, tabuList, commutationMatrix):
    '''
    subList = the list that we actually want to iterate over 
    tabuList = the list of all possible arrangements
    commutationMatrix = ...
    '''

    for listNo in range(len(subList)): 

        # print(listNo)

        tempGatesList = tabuList[listNo]

        # the list of gates of interest if always the one that was appended to the list of possible arrangements last 
        # tempGatesList = tabuList[-1]

        # define a second list, in which only the gateNumber is stored: [[1, [q1, q2]], [2, [q1, q2]], ...] becomes [1, 2, ...]
        gatesList = [gate[0] for gate in tempGatesList]

        # we want to know which matrices commute, so we get all of the indices, corresponding to gates - where matrices commute 
        # commutingGates is a 2d array, where the j-th index of commutingGates[0] and the j-th index of commutingGates[1] commute
        commutingGates = np.where(commutationMatrix)

        # if there is no gate that commutes with another one non trivially, just return 
        if not np.any(commutationMatrix): 
            return tabuList

        newSublist = []

        for i in range(len(gatesList)-1):

            # pick two neighbouring gates. *only* neighbouring gates in the current list are of interest!  
            tempGate1 = gatesList[i]
            tempGate2 = gatesList[i+1]

            # check if they commute by iterating over the commuting gates
            for j in range(len(commutingGates[0])): 

                if tempGate1 == commutingGates[0][j] and tempGate2 == commutingGates[1][j]: 
                    tempList = copy.deepcopy(tempGatesList)

                    # swap the gates
                    tempList[tempGate1], tempList[tempGate2] = tempList[tempGate2], tempList[tempGate1]

                    # if this arrangement is in the list already, continue 
                    if tempList in tabuList: 
                        print('already in list')
                        continue

                    # if not, we append this newly formed list to the collection of lists 
                    tabuList.append(tempList)
                    newSublist.append(tempList)

        # and we perform the BFS on this new list
        tabuList = BFS_Two(newSublist, tabuList, commutationMatrix)

    return tabuList



# newLOPA = BFS([gatesList], commutationMatrix)

# testMatrix = np.zeros((5,5))
# testMatrix[1][2] = 1 
# testMatrix[2][1] = 1
# testMatrix[3][4] = 1
# testMatrix[4][3] = 1
# testMatrix[0][2] = 1
# testMatrix[2][0] = 1

# print(testMatrix)
# test = BFS_Two([[[1],[2],[3],[4],[5]]], [[[1],[2],[3],[4],[5]]], testMatrix)

# print(test)
# print((newLOPA))
# print(newLOPA[0])
# ShowCommutationMatrix(commutationMatrix)
