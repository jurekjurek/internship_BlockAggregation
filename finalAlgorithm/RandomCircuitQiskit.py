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

from qiskit import *
# from qiskit.circuit.random import random_circuit
from AlteredRandomCircuitSourceCode import randomCircuitTwoQubits
from GetMatrixFromCircuit import calculate_circuit_matrix
from qiskit import QuantumCircuit
from qiskit import Aer
from qiskit.extensions import UnitaryGate
import matplotlib.pyplot as plt
import numpy as np




def CreateRandomCircuit(nQubits, nGates, maxNumberOperations):
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

    listOfMatrices = np.zeros(nGates, dtype=object)

    backend = Aer.get_backend('unitary_simulator')
    job = execute(circuitToBeAltered, backend)
    result = job.result()

    listOfMatrices[0] = result.get_unitary(circuitToBeAltered, decimals = 3)

    for iGate in range(nGates-1):

        # if we reached the last gate, we do want to measure 
        if iGate == nGates -2:
            # was true before, but problems with matrix representation 
            tempCirc, involvedQubits = randomCircuitTwoQubits(nQubits, 1, maxNumberOperations, measure=False)
        else:
            tempCirc, involvedQubits = randomCircuitTwoQubits(nQubits, 1, maxNumberOperations, measure=False)


        # backend = Aer.get_backend('unitary_simulator')
        # job = execute(tempCirc, backend, shots=8192)
        # result = job.result()

        # tempMatrix = result.get_unitary(tempCirc,3)

        # print(tempCirc)

        backend = Aer.get_backend('unitary_simulator')
        job = execute(tempCirc, backend)
        result = job.result()
        # print(result.get_unitary(tempCirc, decimals=3))

        listOfMatrices[iGate+1] = result.get_unitary(tempCirc, decimals = 3)


        gatesList.append([iGate+1, involvedQubits])
        

        circuitToBeAltered.barrier()
        circuitToBeAltered = circuitToBeAltered.compose(tempCirc)

        # print(circuitToBeAltered)
        # circuitToBeAltered = circuitToBeAltered + tempCirc

        '''
        for every new part of the circuit, evaluate the matrix and store it in a list of matrices. 
        Then, to check what gate acts on which qubits, look at the rows in the matrices where the matrix is not equal to the unitary matrix. 
        These are the qubits that are being acted on. 
        '''
    
    circuitToBeAltered.draw(output='mpl')

    plt.show()

    print(circuitToBeAltered)

    return gatesList, listOfMatrices

# gatesList, listOfGateMatrices = CreateRandomCircuit(14, 4, 2)

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


def CheckCommutation(matrixOne, matrixTwo): 

    resultOne = np.matmul(matrixOne, matrixTwo)
    resultTwo = np.matmul(matrixTwo, matrixOne)

    if resultOne == resultTwo: 
        return True 
    else: 
        return False 


'''
Maybe write an own random function. 

Assemble random gate strings for each element in number of gates. Store these gates in a list. 
iterate over the gates, check if they commute. 

Only in the end, assemble them to a bigger quantum circuit. 

'''