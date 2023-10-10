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

from qiskit import *
from qiskit.circuit.random import random_circuit
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

def CreateRandomCircuit(nQubits, nGates, maxNumberOperations):

    # first, create one circuit with only one gate 
    circuitToBeAltered = random_circuit(nQubits, 1, maxNumberOperations, measure=False)

    if nGates < 1:
        print('Error, number of gates smaller than one.')
        return 

    print(circuitToBeAltered)

    for iGate in range(nGates-1):

        # if we reached the last gate, we do want to measure 
        if iGate == nGates -2:
            tempCirc = random_circuit(nQubits, 1, maxNumberOperations, measure=True)
        else:
            tempCirc = random_circuit(nQubits, 1, maxNumberOperations, measure=False)

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

CreateRandomCircuit(6, 12, 2)


'''
for i in number of gates: 
    Erstelle einen random circuit mit 20 Qubits und *einem* gate. 
    Appende diesen random circuit to the total circuit 
'''



'''
Maybe write an own random function. 

Assemble random gate strings for each element in number of gates. Store these gates in a list. 
iterate over the gates, check if they commute. 

Only in the end, assemble them to a bigger quantum circuit. 

'''