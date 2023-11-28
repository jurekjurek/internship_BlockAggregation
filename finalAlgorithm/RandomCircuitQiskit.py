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

        # circuitToBeAltered.draw(output = 'mpl')
        # plt.title('COMPLETECIRC')
        # plt.show()

        # print(circuitToBeAltered)
        # circuitToBeAltered = circuitToBeAltered + tempCirc

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
            print('why isnt this working? ')
            print(listOfTempCircuits)
            print(gateNo, otherGateNo)

            circuit1 = listOfTempCircuits[gateNo]
            circuit2 = listOfTempCircuits[otherGateNo]

            print(circuit1)
            print(circuit2)

            # the circuits now consist of two qubits each
            circuit1 = RemoveUnusedQubits(circuit1)
            circuit2 = RemoveUnusedQubits(circuit2)

            print(circuit1)
            print(circuit2)

            testCircuit = QuantumCircuit(3)

            

            print(circuit1)
            print(circuit2)

            # test1Circ = circuit1.compose(circuit2, [0, 1])
            # test2Circ = circuit1.compose(circuit2, [1, 2])

            # print(test1Circ)
            # print(test2Circ)


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

            # if the two circuits do not share any qubits, just continue. They will certainly not commute 
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


            # if circuit1Matrix * circuit2Matrix == circuit2Matrix * circuit1Matrix:
            #     commutationMatrix[gateNo, otherGateNo] = 1

            #     # symmetric
            #     commutationMatrix[otherGateNo, gateNo] = 1

            if CheckCommutation(circuit1Matrix, circuit2Matrix): 

                commutationMatrix[gateNo, otherGateNo] = 1

                # symmetric
                commutationMatrix[otherGateNo, gateNo] = 1








    return gatesList, commutationMatrix

gatesList, commutationMatrix = CreateRandomCircuit(5, 8, 2, display = False)


print(gatesList)

# print(gatesList)
# print(listOfGateMatrices)

# print(listOfGateMatrices)

# print(listOfGateMatrices[0])

# print(type(listOfGateMatrices[0]))
# print(np.shape(listOfGateMatrices[0]))

'''
We arrange the qubits in such a way, that we get as many non-commuting gates in one processing zone as possible 

The goal is to - in the processing zones - arrange as many qubits as possible that do not commute. 
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
        print('Length of final list: ', len(finalList))

    print(finalList)


    return AllowedCircuits


# AllowedArrangements = GetAllValidCircuits(gatesList, commutationMatrix)

# print(AllowedArrangements)

# print(commutationMatrix)

'''
Maybe write an own random function. 

Assemble random gate strings for each element in number of gates. Store these gates in a list. 
iterate over the gates, check if they commute. 

Only in the end, assemble them to a bigger quantum circuit. 

'''