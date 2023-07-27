import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from block_aggregation import *



'''
The layered circuits has been arranged in processing blocks. 
Now, given this setup we can improve upon it using local search algorithms to approximate the ideal placement of the qubits in the individual processing zones. 

What we have now is a list of Processing blocks. So a list of lists of qubits. 
The goal now is to rearrange the qubits in each processing block in such a way that the total number of rearragemets during the actual measuring procedure is minimized. 

For this, we define a metric that is guiding the minimization process. 


The way we approach this optimization problem is: 
0. A function returns a list of Y positions. 
1. We compute the total rearrangement cost for all the processing blocks. At this point we restrict ourselves to associating the qubits solely to their y positions. 
2. Updatestepfunction: swaps the position of two given qubits and returns the list of Y positions as well as the updated total rearrangement cost. 
3. A function ImprovePlacement 



The next step is setting up a tabu search algorithm. 


And the last step is to set up an algorithm that alterantes between tabu search and deterministic search. 


'''



B = blockProcessCircuit(circuit_of_qubits, 10, Fsizes, 4, 1)


print('################################')
print('Optimizing')
print('################################')

# start with a function that returns a list of Y positions given B

def computeArrangements(B, Fsizes, Qmax):
    '''
    Given: 
    '''

    y = []

    for step in range(len(B)): 

        c = B[step][3] 

        y_sublist = []

        for q in range(len(c)): 

            s1, z, k, s2 = c[q]
            
            if s1 == 'p':
                # plot green node at position pos(processing zone 1) + q[2]
                y_temp = - Fsizes[0] - k

                
            elif s1 == 'i':
                # plot red node at position q[1] * pos(storage zone)
                y_temp = - z *  (Fsizes[0] + Qmax)  - k


            y_sublist.append(y_temp)

        # y = y + y_sublist
        y.append(y_sublist)

    return y

y_list = computeArrangements(B, Fsizes, 4)

print(np.shape(y_list))
print(y_list)




def computeTotalCost(Y, Nq):
    '''
    The rearrangement cost is computed based on a metric. 

    This metric shall guide us through the optimization process. 

    Given: 
        Y:  A sequence of Y positions, corresponding to all the qubits in the circuit 
        Nq: Number of qubits in the circuit 

    Returns:
        total rearrangement cost (int)


    '''

    numSteps = len(Y)

    totCost = 0

    for step in range(1, numSteps):
        print('step:', step)

        # look at layers step and step+1
        Yc = Y[step - 1]
        Yf = Y[step]

        # iterate over y positions in both layers 
        # if y position of the qi-th qubit in layer step-1 is not the same as of the qi-th qubit in layer step, add their y distance squared to the total cost 
        for qi in range(Nq):
            totCost += (Yc[qi] - Yf[qi]) ** 2


    # return total cost 
    return totCost  



# test total cost calculation

totalCost = computeTotalCost(y_list, 10)
print(totalCost)





def updateStep(Y, step, q1, q2, totCost):
    '''
    Given the list of Y positions and the layer number (step),
    this function returns a Y list that has qubits q1 and q2 exchanged in this layer and the updatet cost due to the swapping. 
    '''


    numSteps = len(Y)

    newCost = totCost

    # if the layer of interest is not the leftmost layer 
    if step > 0: 

        # subtract the contribution to the total cost caused by the first and second qubit and their left neighbours 
        newCost -= (Y[step][q1] - Y[step - 1][q1]) ** 2 + (Y[step][q2] - Y[step - 1][q2]) ** 2

    # if the layer of interest is not the rightmost layer 
    if step < numSteps-1: 

        # subtract the contribution to the total cost caused by the first and second qubit and their right neighbours 
        newCost -= ( Y[step][q1] - Y[step+1][q1] ) ** 2 + (Y[step][q2] - Y[step+1][q2]) ** 2
    
    # swap qubits in layer
    temp = Y[step][q1]
    Y[step][q1] = Y[step][q2]
    Y[step][q2] = temp


    # add cost due to the new constellation of qubits, equal procedure as above. 
    if step > 1:
        newCost += (Y[step][q1] - Y[step - 1][q1])**2 + (Y[step][q2] - Y[step - 1][q2])**2

    if step < numSteps:
        newCost += (Y[step][q1] - Y[step + 1][q1])**2 + (Y[step][q2] - Y[step + 1][q2])**2

    
    return newCost, Y

print(y_list)

newCost, Y_new = updateStep(y_list, 2, 2, 3, totalCost)


print(Y_new)


def improvePlacement(BP, Nq, Fsizes, Qmax, Mmax, echo):
    '''
    This function improves the placement of the qubits, subsequently minimizing the metric used in the function 
    computeTotalCost()
    this function will be referred to as the deterministic part of the optimization procedure. 
    
    Given: 
    BP: 
    Nq: 

    Returns: 
        Updated list bNew of qubits in processing blocks 
        List of total rearrangemet cost per iteration for displaying reasons


    '''

    # firstly, define variables of interest

    # list of Y positions of qubits
    Y = computeArrangements(BP, Fsizes, Qmax)

    # total cost to start with (of the initial qubit constellation)
    costTot = computeTotalCost(Y, Nq)

    # number of processing blocks
    numSteps = len(BP)

    # number of storage zones 
    numF = len(Fsizes)
    
    # copy of B to be manipulated
    bNew = BP

    '''
    There are different types of swaps that can be done. Of course, we cannot swap active qubits from a processing zone with qubits in storage zones. 
    '''

    for step in range(2, numSteps):
        
        # 1. swap idle qubits between storage zones
        for z in range(numF):

            SP, GP, FP, c = bNew[step]

            # iterate over all idle qubits 
            for qi in range(len(FP[z])):

                q = FP[z][qi]

                zp = cp[q][2]





    return True



