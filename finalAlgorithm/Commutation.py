from RandomCircuitQiskit import *

# create a random circuit 
randomCircuit, gatesList, listOfTempCircuits = CreateRandomCircuit(5, 5, 2, False)


def DoGatesCommute(gateOne, gateTwo, listOfTempCircuits):
    '''
    gateOne = format [gate, [q1, q2]]
    gateTwo = same format 
    listOfTempCircuits = list of the gates that make up the circuit

    returns a boolean indicating if the two gates commute or not 
    '''

    q1, q2              = gateOne[1]
    otherQ1, otherQ2    = gateTwo[1]


    # create two circuits based on the gates circuit representation (stored in tempcircuitList) 
    # and see if the corresponding matrices commute
    circuit1 = listOfTempCircuits[gateOne[0]]
    circuit2 = listOfTempCircuits[gateTwo[0]]

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
        return True  

    
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
        return True

    else:
        return False 

