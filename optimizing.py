import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from block_aggregation import *



'''
The layered circuits has been arranged in processing blocks. 
Now, given this setup we can improve upon it using local search algorithms to approximate the ideal placement of the qubits in the individual processing zones. 

This programme starts with a variable B. This variable is composed as follows: 

B = [[SP, GP, FP, c], ..., [SP,GP,FP,c]] where len(B) = number of processing blocks. 

let us remind ourselves what exatly these different constituents are: 

SP = contains the qubits in the processing zones 
GP = contains the gates covered by these qubits 
FP = contains qubits in the storage zones 
c = {s, m, k, s'}, where: 
    s = {'p', 'i'}:  indicates if q is stored in processing zone or idle pool 
    m = {0, ...}  processing zone number 
    k = {1, ...} position within processing zone or idle pool 
    s'= {'a', 'i'} active or idle (within processing zone, the qubits in idle pool are always idle / inactive.)

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

    # list of Y positions of qubits for all the processing blocks, shape: shape(Y) = (num_processing_blocks, num_qubits)
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

    # Iterate over the processing blocks, in original file we stared at one but I guess its fine 
    for step in range(numSteps):


        # get information from previous step to compare to current step 
        SPp, GPp, FPp, cp = bNew[step-1]

        # if we have not reached the end of the blocks yet, also define the right partner
        if step < len(BP)-1:

            # variables for the processing block on the right 
            SPf, GPf, FPf, cf = bNew[step+1]
        



        '''
        1. swap idle qubits between storage zones
        '''

        # iterate over all the storage zones 
        for z in range(numF):

            SP, GP, FP, c = bNew[step]

            # iterate over all idle qubits in the z-th storage zone 

            # For all the qubits, we look at them in the processing blocks left and right to it. Why? 
            # To determine if it makes sense to swap them with qubits 

            # We want to swap qubits q1 and q2 in step step. 
            # Therefore, we examine a couple of things of q1 and q2 in the previous and next steps 


            for qi in range(len(FP[z])):

                # qi-th qubit in z-th storage zone 
                q = FP[z][qi]

                # processing/storage zone number of the previous block! 
                zp = cp[q][1]

                # in idle or processing zone in previous block? 
                s1p = cp[q][0]

                # processing zone number and zone indicator for qubit in the right processing block 
                if step < len(BP)-1:
                    zf =  cf[q][2]
                    s1f = cf[q][1]

                # if previous qubit is not idle, or the qubit in the previous processing block is in the same storage zone as the qubit in this processing block 
                if s1p != 'i' or zp == z:
                    continue

                # iterate over all previous storage zone qubits as possible swap partners 
                for qi2 in range(len(FP[zp])):

                    # qubit two, the qubit we want to exchange qubit 1 with 
                    q2 = FP[zp][qi2]

                    # we cannot swap a qubit with itself 
                    if q2 == q: 
                        continue 
                    
                    # Processing zone number of qubit 2 in previous step 
                    z2p = cp[q2][2]

                    # Is qubit 2 in idle or in processing zone in previous step
                    s12p = cp[q2][1]

                    # if we have not reached the rightmost layer, define z and s for the right neighbour (next step) as well 
                    if step < len(BP)-1:

                        # processing zone number and indication in which kind of zone for qubit 2 in next step 
                        z2f = cf[q2][2]
                        s12f = cf[q2][1]

                    # if qubit 1 and 2 are in the same storage zone and are both idle (we know that q1 is idle anyway, but we dont know this for q2 for the previous step yet), continue 
                    # (it could also be that one is stored in a processing zone and the other one in a storage zone. In this case, z2p == zp would not mean that they are in the same zone)
                    if z2p == zp and s12p == 'i':
                        continue

                    # if, in the next step, q1 and q2 are in the same storage zone, continue 
                    if step < numSteps: 
                        if z2f == zf and s12f == 'i':
                            continue
                    

                    # if none of the continues above have been executed, we swap qubit one and two in bNew and in the Y list 

                    # swap q and q2 in bNew, a few lines, add later 
                    # 1. Swap values in the sublist at the 4th position of BPnew, corresponding to c 
                    BPnew[step][3][q], BPnew[step][3][q2] = c[q2], c[q]

                    # 2. Swap qubit indices in the sublist at the 3rd position of BPnew for 'z'
                    BPnew[step][2][z] = [q2 if x == q else x for x in BPnew[step][2][z]]

                    # 3. Swap qubit indices in the sublist at the 3rd position of BPnew for 'zp'
                    BPnew[step][2][zp] = [q if x == q2 else x for x in BPnew[step][2][zp]]

                    # swap q1 and q2 in Y and update the costTot
                    costTot, Y[step] = updateStep(Y, step, q, q2, costTot)

                    break 

        
        '''
        2. Swap idle qubits within idle zones to minimize swaps 
        '''
        # similar to above, but we iterate twice over the same idle zone 

        # z is storage zone number! 
        for z in range(numF):

            SP, GP, FP, c = bNew[step]

            # iterate over all idle qubits 
            for qi in range(len(FP[z])):

                #  qi-th qubit in the z-th storage zone, up until here everyting is the same as above
                q1 = FP[z][qi]

                # Now different: We have to take into account the position in the storage zone 
                k = c[q1][2]

                # processing zone number of previous block, qubit one 
                zp = cp[q1][1]

                # is qubit one previously in idle or in processing zone? 
                s1p = cp[q1][0]

                # What position does qubit one have in the previous step in a storage zone? 
                kp = cp[q1][2]


                # if qubit is not idle, or if previous processing zone and current processing zone are not equal
                if s1p != 'i' or zp != z:
                    continue

                # iterate over all qubits in the *same* storage zone as possible swap partners 
                for qi2 in range(len(FP[z])):

                    if qi == qi2: 
                        continue

                    # swap partner for q1
                    q2 = FP[z][qi2]

                    # we still cannot exchange the same qubit with itself
                    if q2 == q1: 
                        continue 

                    # previous processing zone number of qubit 2 
                    z2p = cp[q2][2]

                    # was qubit two in processing or storage zone in previous step? 
                    s12p = cp[q2][1]


                    # if, in previous step, q1 and q2 were not in the same processing zone or second qubit is not idle
                    if z2p != zp or s12p != 'i':
                        continue

                    # position for qubit two 
                    k2 = c[q2][3]

                    # previous position for qubit two 
                    k2p = cp[q2][3]

                    # compute a distance: 
                    # distance from qubit 1 in previous step to qubit one in this step 
                    # and distance from qubit 2 in previous and this step 
                    dist = (k-kp)**2 + (k2-k2p)**2

                    # And then: 
                    # Distance between q1 in this step and q2 in previous step 
                    # and distance between q2 in this and q1 in previous step 
                    distSwap = (k-k2p)**2 + (k2-kp)**2

                    # if the distance for the swapped case of q1 and q2 is bigger or equal to dist, continue 
                    if not distSwap < dist:
                        continue

                    # if swapping decreases the distance, exchange these two qubits with each other 
                    
                    # swap pointers 
                    bNew[step][3][q1] = c[q2]
                    bNew[step][3][q2] = c[q1] 

                    # swap qubits in storage zones (B = [[SP, GP, FP, c], ..., []]), so second index of B 
                    bNew[step][2][z][qi] = q2
                    bNew[step][2][z][qi2] = q
                    
                    
                    # update total cost and swap qubits in Y list 
                    costTot, Y[step] = updateStep(Y, step, q, q2, costTot)

                    break 


        '''
        3. Swap entire processing zones to minimize swaps 
        '''

        

        # as opposed to numF, the number of storage zones, we now iterate over the processing zones 
        # -> z is processing zone number 
        for z in range(Mmax):

            # small comment: when there's only one processing zone, this step obviously does not make any sense and is skipped 
            if Mmax == 1:
                continue


            # this is defined *in* the for loop since bNew alters during the course of the for loop
            SP, GP, FP, c = bNew[step]

            # The list of interest is now SP, which contains the qubits in the processing zones #
            # in the easiest case, we only have one processing zone which means: SP = [[q1,q2,q3,q4,q5]] with five qubits 
            # SPz is now the list of qubits in the z-th processing zone 
            SPz = SP[z]
            # print(SPz)

            # I actually dont understand why we have to flatten here, look at this again.

            # iterate over all processing zones, in order to swap processing zone with processing zone 
            for z2 in range(Mmax):

                # not possible to swap the same processing zones 
                if z == z2: 
                    continue
                
                # in the code, this is again flattened 
                # list of qubits in the second processing zone 
                SPz2 = SP[z2]

                # in mathematica, this is one expression, using np probably too 
                dist = 0
                # iterate over all the qubits in the processing zones 
                for qi in range(Qmax):

                    # compute distance from the previous layers position of qubit 1 and 2 for all the qubits 
                    dist += ( Y[step][SPz[qi]] - Y[step-1][SPz[qi]] )**2 + ( Y[step][SPz2[qi]] - Y[step-1][SPz2[qi]] )**2

                # now, the same for distswap
                distswap = 0
                for qi in range(Qmax):

                    # if we were to swap, how would the distances look like? 
                    distswap += ( Y[step, SPz2[qi]] - Y[step-1, SPz[qi]] )**2 + ( Y[step, SPz[qi]] - Y[step-1, SPz2[qi]] )**2
                
                # if swapping actually decreases the distance 
                if distswap < dist:
                    # the two processing zones are swapped 
                    # first, in the list bNew, so essentially we swap the elements in the SP list 

                    temp_b = bNew[step][0][z]
                    bNew[step][0][z] = bNew[step][0][z2]
                    bNew[step][0][z2] = temp_b

                    # c[1], so the processing zone number is changed as well. That's all that changes for the qubits 
                    for qi in range(Qmax):
                        bNew[step][3][SPz[qi]][1] = z2
                        bNew[step][3][SPz2[qi]][1] = z

                        # we have to do this in the for loop, because we can always only swap two qubits, not a set of qubits - maybe np.vectorize at some point 
                        costTot, Y[step] = updateStep(Y, step, numSteps, SPz[qi], SPz2[qi], costTot)

                    break

            

        '''
        4.  Swap qubits within processing zones to minimize swaps
            Swapping qubits in between processing zones does not make any sense obviously, since the corresponding gates do not commute 
        '''

        # again, iterate over processing zones 
        for z in range(Mmax):


            SP, GP, FP, c = bNew[step]
            
            # list of qubits in z-th processing zone 
            SPz = SP[z]

            # iterate over all qubits in z-th processing zone 
            ##############################################################################################################################
            # Ich habe wahrscheinlich noch nicht so ganz verstanden, warum wir einmal ueber Qmax und einmal ueber len(SPz) iterieren!!!! #
            ##############################################################################################################################

            for qi in range(Qmax):

                # i-th qubit in z-th processing zone 
                q1 = SPz[qi]

                # position of q1 in processing zone z
                k = c[q1][2]

                # previous processing zone of qubit 
                zp = cp[q1][1]

                # previous zone of qubit 
                s1p = cp[q1][0]

                # previous position in zone of qubit 
                kp = cp[q1][2]

                # if this qubit is not in a processing zone, for whatever reason or the storage zones between this and previous step did not change, no need to switch this qubit 
                if s1p != 'p' or zp != z:
                    continue 

                # iterate over all qubits in the same processing zone 
                for qi2 in range(len(SPz)):

                    # dont exchange the same qubit 
                    if qi == qi2: 
                        continue

                    # qubit 2 to be swapped with qubit 1 
                    q2 = SPz[qi2]

                    # this is somehow different to the one above 
                    if q2 == q1: 
                        continue

                    # in what kinda zone? Has to be 'p'
                    s12p = cp[q2][0]

                    # processing zone number
                    z2p  = cp[q2][1]

                    # if processing zone number of q1 is not the same as processing zone number of q2 in previous step, continue  
                    if s12p != 'p' or z2p != z: 
                        continue 

                    # position of q2 in this step 
                    k2 = c[q2][2]

                    # position of q2 in previous step 
                    k2p = cp[q2][2]

                    # look at qubit one and two and their respective differences to the previous layers 
                    dist = (k-kp)**2 + (k2-k2p)**2

                    # and here in case of a swap 
                    distSwap = (k-k2p)**2 + (k2-kp)**2

                    # not important 
                    if echo == True: 
                        print(" candidates - z: ", z, " zprev: ", zp, " z2prev: ", z2p, " q: ", q, " q2: ", q2)


                    # if we cant improve, just keep going 
                    if not (distSwap < dist):
                        continue


                    if echo == True:
                        print("  swap found - dist: ", dist, " distSwap: ", distSwap)


                    # all that is exchanged between those two qubits is the position inside the processing zone. This is the only part of the pointerlist c that we have to update 
                    bNew[step][3][q1][2] = k2
                    bNew[step][3][q2][2] = k

                    costTot, Y[step] = updateStep(Y, step, numSteps, q1, q2, costTot)

                break 

    # here, more parameters are returned in the future, for debugging and displaying reaasons 
    return bNew    


improvePlacement(B, 10, Fsizes, 4, 1, True)


'''
This is it for the algorithm! 

Here, one can further investigate the developement of the totalcost with the swaps done. What we did now is we just swapped two qubits when the metric was okay with it. 
The function does this once. This means: The function does this for every layer and every qubit in every layer. And looks at every qubit in every layer as a potential swapping partner.
'''



