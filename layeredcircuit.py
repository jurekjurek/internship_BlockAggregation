import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.lines import Line
# from matplotlib.patches import Circle
import random
import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister


def LayerCircuit(Nq, circ, search_horizon = 10):
    '''
    This function creates a list of layers with mutually commuting gates inside. 
    At each iteration, an empty layer is created and filled with gates in the course of iterating over the circ list. 

    Returns list of gates. 

    '''
    LayeredCircuit = []
    usedgates = []
    
    # if not all gates have been examined, continue
    while len(usedgates) != len(circ):
        # print(len(usedgates))

        # within each new element in the layered circuit, create a new layer. 
        layer = []
        blockedqubits = []
        g = 0

        # iterate over elements in the circuit and fill the layers with mutually commuting gates
        while len(blockedqubits) != Nq and g < len(circ):

            # has this gate in the circuit been used already? If not, 
            if g not in usedgates: 

                # first of all, we only consider a certain amount of gates
                if layer != [] and g-layer[0][0] > search_horizon: 
                    g += 1
                    continue  
                # look at the individual qubits 
                q1 = circ[g][1][0]
                q2 = circ[g][1][1]

                # if the qubits are not blocked, we can append the gate to the layer 
                if q1 not in blockedqubits and q2 not in blockedqubits: 

                    # add gate to layer 
                    # layer.append(g)

                    layer.append([g, [q1,q2]])

                    # mark gate as used 
                    usedgates.append(g)

                    # block the qubits for this layer 
                    blockedqubits.append(q1)        # only in this layer!
                    blockedqubits.append(q2)

            # now, for the next layer 
            g += 1
        
        LayeredCircuit.append(sorted(layer))
        LayeredCircuit_np = np.array(LayeredCircuit)

    return LayeredCircuit_np



def show_layeredCircuit(Nq, circ, layeredcirc):
    '''
    This function uses qiskit to display a circuit with Nq qubits. The gates are displayed as dictated by the circ list created in the function random_circuit. 
    '''
    q_a = QuantumRegister(Nq, name='q')
    circuit = QuantumCircuit(q_a)
    for i in range(len(layeredcirc)):
        for g in layeredcirc[i]:

            circuit.cz(q_a[circ[g][1][0]-1], q_a[circ[g][1][1]-1], label=str(g+1))
        circuit.barrier()
    circuit.draw(output='mpl', justify='none', fold = 50)
    plt.show()
    # print(circuit)


# show_layeredCircuit(10, circuit_of_qubits, layeredcircuit)
