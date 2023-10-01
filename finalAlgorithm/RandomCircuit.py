import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.lines import Line
# from matplotlib.patches import Circle
import random
import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister



def random_circuit(Nq, Dg):
    '''
    Nq = number of qubits
    Dg = number of gates

    This function returns a np.array of gatenumbers with corresponding qubit numbers. 
    [[GateNo, [QubitNo1, QubitNo2]], [...], ..., [...]]

    It creates a random circuit. Based on the format in which we will get the raw circuit, we can adjust the function to return the raw circuit in the desired form. 

    '''
    circ = np.zeros((Dg, 2), dtype=object)
    
    for i in range(Dg):

        # choose two integers corresponding to two qubits in the range 1, Number of Qubits without replacement. So the same number does not occur twice. 
        QB_list = random.sample(range(Nq), 2)

        QB_array = np.array(QB_list)

        circ[i] = np.array([i, np.sort(QB_array)])
    
    return circ



def show_circuit(Nq, circ):
    '''
    This function uses qiskit to display a circuit with Nq qubits. The gates are displayed as dictated by the circ list created in the function random_circuit. 
    '''

    q_a = QuantumRegister(Nq, name='q')
    circuit = QuantumCircuit(q_a)
    
    for g in range(len(circ)):

        circuit.cz(q_a[circ[g][1][0]], q_a[circ[g][1][1]], label=str(g+1))
    circuit.draw(output='mpl', fold = 50)#, justify='none')
    plt.show()
    print(circuit)
