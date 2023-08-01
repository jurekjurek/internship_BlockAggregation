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

# list of y positions is returned correctly 
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
print('totalcost:',totalCost)


# exit()


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

print(y_list, totalCost)

newCost, Y_new = updateStep(y_list, 2, 2, 3, totalCost)

print(Y_new, newCost)


# exit()

def improvePlacement(BP, Nq, Fsizes, Qmax, Mmax, echo):
    '''
    This function improves the placement of the qubits, subsequently minimizing the metric used in the function 
    computeTotalCost()
    this function will be referred to as the deterministic part of the optimization procedure. 
    
    Given: 
    BP:     a list of Blocks and their corresponding variables S, G, c, 
    Nq:     Number of total qubits
    Fsizes: Sizes of the storage zones 
    Qmax:   Maximum amount of qubits in processing zones 
    Mmax:   Number of processing zones in processing block 
    echo:   Do we want to print (debugging reasons)

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
    
    at every iteration, we safe the best BP so far, as well as the totcost. In the mathematica file, the expressions:
        Sow[costTot, 1];
        Sow[BPnew, 2];
    safe these values for every iteration corresponding to the index 1 and 2. The reap and sow in the original file is only done for displaying reasons. 

    this function is split into four parts: 
        1. swap idle qubits between differennt idle ones to prevent crossings. 
        2. Swap idle qubits within idle zones to minimize the number of swaps possible in experiment 
        3. Swap whole processing zones 
        4. Swap qubitts within processing zones to minimize number of swaps needed. 

    '''

    # why start at one? 
    for step in range(1, numSteps):


        # get information from previous step to compare to current step 
        SPp, GPp, FPp, cp = bNew[step-1]

        # if we have not reached the end of the blocks yet, also define the right partner
        if step < len(BP)-1:
            SPf, GPf, FPf, cf = bNew[step+1]
        
        # 1. swap idle qubits between storage zones
        for z in range(numF):

            SP, GP, FP, c = bNew[step]

            # iterate over all idle qubits 
            for qi in range(len(FP[z])):

                q = FP[z][qi]

                zp = cp[q][2]

                s1p = cp[q][1]

                if step < len(BP):
                    zf =  cf[q][2]
                    s1f = cf[q][1]

                # if qubit is not idle, or we want to switch the same qubit, which is not possible
                if s1p != 'i' or zp == z:
                    continue

                # iterate over all storage zone qubits as possible swap partners 
                for qi2 in range(len(FP[zp])):
                    q2 = FP[zp][qi2]

                    if q2 == q: 
                        continue 

                    z2p = cp[q2][2]
                    s12p = cp[q2][1]

                    if step < len(BP):
                        z2f = cf[q2][2]
                        s12f = cf[q2][1]


                    if z2p == zp and s12p == 'i':
                        continue


                    if step < numSteps: 
                        if z2f == zf and s12f == 'i':
                            continue
                    
                    # swap q and q2 in bNew, a few lines, add later 
                    # bNew[step][4] = 

                    costTot = updateStep(Y, step, q, q2, costTot)

                    break 

        
        # 2. Swap idle qubits within idle zones to minimize swaps 
        # similar to above, but we iterate twice over the same idle zone 

        for z in range(numF):

            SP, GP, FP, c = bNew[step]

            # iterate over all idle qubits 
            for qi in range(len(FP[z])):

                q = FP[z][qi]

                k = c[q][3]

                zp = cp[q][2]

                s1p = cp[q][1]

                kp = cp[q][3]


                # if qubit is not idle, or we want to switch the same qubit, which is not possible
                if s1p != 'i' or zp != z:
                    continue

                # iterate over all qubits in the *same* storage zone as possible swap partners 
                for qi2 in range(len(FP[z])):

                    if qi == qi2: 
                        continue

                    q2 = FP[z][qi2]

                    # we still cannot exchange the same qubit with itself
                    if q2 == q: 
                        continue 

                    z2p = cp[q2][2]
                    s12p = cp[q2][1]



                    if z2p != zp or s12p != 'i':
                        continue

                    k2 = c[q2][3]

                    k2p = cp[q2][3]

                    dist = (k-kp)**2 + (k2-k2p)**2

                    distSwap = (k-k2p)**2 + (k2-kp)**2

                    if not distSwap < dist:
                        continue

                    
                    # Same as above: Swap q and q2 in bNew, a few lines, add later 
                    # bNew[step][4] = 

                    costTot = updateStep(Y, step, q, q2, costTot)

                    break 











        # 3. Swap entire processing zones to minimize swaps 

        for z in range(Mmax):

            SP, GP, FP, c = bNew[step]

            # in this step, we flatten a list, looks bad but it will look better when using np
            SPz = SP[z]
            print(SPz)

            # I actually dont understand why we have to flatten here, look at this again.

            for z2 in range(Mmax):
                if z == z2: 
                    continue
                
                # in the code, this is again flattened 
                SPz2 = SP[z2]

                # in mathematica, this is one expression, using np probably too 
                dist = 0
                for qi in range(Qmax):
                    dist += ( Y[step, SPz[qi]] - Y[step-1, SPz[qi]] )**2 + ( Y[step, SPz2[qi]] - Y[step-1, SPz2[qi]] )**2

                # now, the same for distswap
                distswap = 0
                for qi in range(Qmax):
                    distswap += ( Y[step, SPz2[qi]] - Y[step-1, SPz[qi]] )**2 + ( Y[step, SPz[qi]] - Y[step-1, SPz2[qi]] )**2
                

                if distswap < dist:

                    # change the two qubits in the new B: 
                    # bNew[step][]

                    for qi in range(Qmax):
                        bNew[step][4][SPz[qi]][2] = z2
                        bNew[step][4][SPz2[qi]][2] = z
                        costTot, Y[step] = updateStep(Y, step, numSteps, SPz[qi], SPz2[qi], costTot)

                    break

                

            # just switch to numpy at this point... 







        # 4. Swap qubits within processing zones to minimize swaps

        for z in range(Mmax):
            SP, GP, FP, c = bNew[step]
            
            # this was also flattened 
            SPz = SP[z]

            q = SPz[qi]

            k = c[q][3]

            zp = cp[q][2]

            s1p = cp[q][1]

            kp = cp[q][3]


            if s1p != 'p' or zp != z:
                continue 

            for qi2 in range(len(SPz)):
                if qi == qi2: 
                    continue

                q2 = SPz[qi2]

                if q2 == q: 
                    continue

                s12p = cp[q2][1]
                z2p  = cp[q2][2]

                # if q2 not in same processing zone in previous step, do not swap 
                if s12p != 'p' or z2p != z: 
                    continue 

                k2 = c[q2][3]

                k2p = cp[q2][3]

                dist = (k-kp)**2 + (k2-k2p)**2

                distSwap = (k-k2p)**2 + (k2-kp)**2

                if echo == True: 
                    print(" candidates - z: ", z, " zprev: ", zp, " z2prev: ", z2p, " q: ", q, " q2: ", q2)


                # if we cant improve, just keep going 
                if not (distSwap < dist):
                    continue


                if echo == True:
                    print("  swap found - dist: ", dist, " distSwap: ", distSwap)

                bNew[step][4][q][3] = k2

                bNew[step][4][q2][3] = k

                costTot, Y[step] = updateStep(Y, step, numSteps, q, q2, costTot)

                break 

    # here, more parameters are returned in the future 
    return bNew    


improvePlacement(B, 10, Fsizes, 4, 1, True)




