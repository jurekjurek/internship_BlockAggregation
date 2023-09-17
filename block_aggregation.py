import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.lines import Line
# from matplotlib.patches import Circle
import random
import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import math 

import matplotlib.animation as animation

import networkx as nx
from fancify_text import italic, bold, italicSerif
 
from randomcircuit import * 
from layeredcircuit import * 

'''
In this file, the mathematica file ... 
will be transcripted into python, extended and commented in order for other people to be able to use it. 

There are a few important files involved in this project. 
The first one is randomcircuit.py - it creates a random circuit and plots it using qiskit. 

The second one is layeredcircuit.py - it creates a layered circuit given a raw circuit as input 

The third one is blockprocessing.py - it applies the block aggregation algorithm to the layered circuit. 

What is also of interest is: 
    1. The commutation rule: Not only do two gates commute if they just do not share two qubits. It is possible to have more general commutation rules. Implement this. 
    2. 

'''

NQ = 20
GATES = 40
MMAX = 2
QMAX = 4
FSIZES = [4,4,4]


circuitOfQubits = random_circuit(NQ, GATES)

# show_circuit(10,circuit_of_qubits)

layeredCircuit = LayerCircuit(10, circuitOfQubits)
# show_layeredCircuit(10, circuit_of_qubits, layeredcircuit)


'''
Now that we have the layered circle going, we can focus on the block aggregation. 
This will be done ... 

Structure: 
Aggregation step - Postprocessing step - Qubit Placement - ...
repeat until termination condition is satisfied 

'''

def EvaluateGateCoverage(S, G, nQ, qMax, mMax):
    '''
    evaluates gate coverage given: 
        1. S: A set of qubit sets S
        2. G: A gate Coverage set G
        3. nQ: The total number of qubits 
        4. qMax: The maximal number of qubits in a processing zone qMax  
        5. mMax: The maximal number of processing zones mMax

    returns two ints gateCoverage and qubitNonCoverage, indicating 
        1. gateCoverage: how many gates are covered with this constellation and 
        2. qubitNonCoverage: the number of qubits that are in sets that are bigger than the maximum number of qubits in a processing zone. These qubits cannot be covered anymore

    The gateCoverage is to be maximized in the course of this algorithm 

    '''

    # initialize variables of interest to zero 
    gateCoverage = 0

    # Number of qubits that cannot be covered, because the corresponding sets are larger than the maximal number of Qubits in a processing zone Q
    qubitNonCoverage = 0

    # define running variable 
    processingZoneNo = 1

    # iterate over elements in qubit sets 
    for n in range(len(S)):

        # if one specific set of qubits has more elements than can be stored in the processing zone, the number of qubits that cannot be covered is increased 
        if len(S[n]) > qMax: 
            qubitNonCoverage += len(S[n])

        # if the number of qubits in a set is still in the range of possible qubits in a processing zone, and we populate one of the possible processing zones whose number is limited by mMax:
        if len(S[n]) <= qMax and processingZoneNo <= mMax: 

            # we increase the gatecoverage 
            gateCoverage += len(G[n])

            # and we jump to the next processing zone 
            processingZoneNo += 1  

    return gateCoverage, qubitNonCoverage



# def InitBlockAggregation():
#     S = []
#     G = []
#     c = []
#     S_b = []
#     G_b = []
#     return S, G, c, S_b, G_b


'''

G_n, so one specific element of the G list indicates what gates are covered by the Qubit Set S_n  
mMax is the number of processing zones in one processing block 

'''

def AggregateBlocksStep(layeredCirc, nQ, qMax, mMax):
    '''
    The goal is to find the set of S and G that produce the best GateCoverage!!

    Given: 
        layeredcirc:        A circuit, arranged in layers 
        nQ:                 Number of qubits in the circuit
        qMax:               Maximum number of qubits in a processing zone 
        mMax:               Maximum number of processing zones 

    Returns: 
        SBest:              Set of qubits that maximize the gatecoverage
        GBest:              Gates covered by the set of qubits that maximize the gatecoverage 
        gateCoverageList:   For displaying purposes of the course of the algorithm 

    '''

    # S is a list of lists! G is a list of lists! 
    # At the beginning, S is of length nQ, but in the course of the algorithm, the qubits as well as the gates are merged together and S gets shorter with increasingly bigger elements.


    # before starting the iteration over layers and gates, initialize the S and G lists
    # The s list, the list containing the qubits, will be initialized as follows: S = [[1],[2],...], so the first qubit set contains only the first qubit, the second set only the second qubit and so on
    aggregatedQubits = [[n] for n in range(nQ)]


    # same for the gate coverage sets
    gatesCovered = [[] for _ in range(nQ)]

    # also the pointer variables will be initialized, in the beginning cn = n, because every qubit has its own set S_n, later the sets will get merged and more qubits will have the same cn
    pointerTable = [n for n in range(nQ)]


    # shall be overwritten quickly, 
    aggregatedQubitsBest = []
    gatesCoveredBest = []

    # initialize gate coverage counter, the variable to be maximized
    bestGateCoverage = 0

    # for debugging
    gateCoverageList = []

    # iterate over layers 
    for layerNumber in range(len(layeredCirc)):

        # iterate over gates in layers 
        for gateNumber in range(len(layeredCirc[layerNumber])):

            gate = layeredCirc[layerNumber][gateNumber]
            
            # define qubit one and two, that are part of the gate gateNumber in layer layerNumber 
            firstGateQubit = gate[1][0]
            secondGateQubit = gate[1][1]

            # To what qubit set do the two qubits belong? 
            pointerFirstGateQubit = pointerTable[firstGateQubit]
            pointerSecondGateQubit = pointerTable[secondGateQubit]

            
            # append gate (which is not just a number) to gate coverage set of qubit set corresponding to cn
            if gatesCovered[pointerFirstGateQubit] != []:
                gatesCovered[pointerFirstGateQubit].append(gate[0])
            if gatesCovered[pointerFirstGateQubit] == []:
                gatesCovered[pointerFirstGateQubit] = [gate[0]]
            

            # if cn and cm are equal, meaning they are part of the same qubit set, continue
            if pointerFirstGateQubit == pointerSecondGateQubit: 
                continue        # we don't have to merge the Qubit sets 

            # Merge Qubit sets
            # We always merge the smaller to the larger set. So if the set belonging to cm is larger than the set belonging to cn, swap them 
            if len(aggregatedQubits[pointerFirstGateQubit]) < len(aggregatedQubits[pointerSecondGateQubit]):
                temp = pointerSecondGateQubit
                pointerSecondGateQubit = pointerFirstGateQubit 
                pointerFirstGateQubit = temp

            # We merge the qubit sets together
            aggregatedQubits[pointerFirstGateQubit] = aggregatedQubits[pointerFirstGateQubit] + aggregatedQubits[pointerSecondGateQubit]

            # And we merge the gate coverage sets together
            # Remember: Gate n connects qubits n and m, so we dont have to append the gate to G[cm] as well, if we did, we would have it twice 
            gatesCovered[pointerFirstGateQubit] = gatesCovered[pointerFirstGateQubit] + gatesCovered[pointerSecondGateQubit]


            # All the pointers that belonged to the qubits in set S[cm] will now be pointing to set S[cn]
            for qubitNo in range(len(aggregatedQubits[pointerSecondGateQubit])):

                # qubits are just numbers in the code, so S[cm][i] returns exactly the n-th qubit of all qubits. 
                pointerTable[aggregatedQubits[pointerSecondGateQubit][qubitNo]] = pointerFirstGateQubit     # all elements in S[cm] which represent qubits stored as numbers are assigned an element in the pointerTable list corresponding to cn

            # The qubit set S[cm] is emptied 
            aggregatedQubits[pointerSecondGateQubit] = []

            # The gate coverage set corresponding to Set cm is emptied, because it was merged above
            gatesCovered[pointerSecondGateQubit] = []

            # Remember: S is sorted list and G is a sorted list
            # They are sorted by size; biggest qubits sets as first elements, biggest gate coverage sets as first elements

            # first, let's take care of the set cn that we appended stuff to:
            # if cn is not the first element in the list already (if we append something to the biggest element, it stays the biggest element), we dont have to do anything 
            if pointerFirstGateQubit > 0:

                # we want to move the qubit to the appropriate position in aggregatedQubits. Compare to the element that is one element after it in the list. If it is bigger, move S[cn] up one element
                while (len(aggregatedQubits[pointerFirstGateQubit]) > len(aggregatedQubits[pointerFirstGateQubit-1]) and pointerFirstGateQubit != 0) or gatesCovered[pointerFirstGateQubit-1] == None:
                    
                    # in the pointer list pointerTable, assign cn to all elements that are assigned cn - 1

                    # What's happening here is essentially swapping all the elements in the lists pointerTable, G and S accordingly. 

                    # remember: We effectively move S[] up in the set of qubits S, so upon moving up one step, we effectively replace S[cn] and S[cn-1] as well as the pointers that point to them;
                    # the pointers of the qubits that are stored in set cn will become cn-1 and vice versa 
                    for k in range(len(aggregatedQubits[pointerFirstGateQubit])):
                        pointerTable[aggregatedQubits[pointerFirstGateQubit][k]] = pointerFirstGateQubit - 1

                    for k in range(len(aggregatedQubits[pointerFirstGateQubit-1])):
                        pointerTable[aggregatedQubits[pointerFirstGateQubit-1][k]] = pointerFirstGateQubit


                    # swap the two elements S[cn] and S[cn-1], effectively moving S[cn] up one element in the list. 
                    templist = aggregatedQubits[pointerFirstGateQubit]
                    aggregatedQubits[pointerFirstGateQubit] = aggregatedQubits[pointerFirstGateQubit-1]
                    aggregatedQubits[pointerFirstGateQubit-1] = templist

                    # swap the two elements G[cn] and G[cn-1]
                    templist = gatesCovered[pointerFirstGateQubit]
                    gatesCovered[pointerFirstGateQubit] = gatesCovered[pointerFirstGateQubit-1]
                    gatesCovered[pointerFirstGateQubit-1] = templist 

                    pointerFirstGateQubit -= 1

            # now, for the second list element corresponding to the pointer cm 
            # if cm is not the last element in the list already (if we clear the last element of the list, )
            # We cannot just append [] to the end of S and G, since we have to move the stuff inside the pointerTable list as well

            if pointerSecondGateQubit < nQ-1:

                while len(aggregatedQubits[pointerSecondGateQubit+1]) > 0:
                    for k in range(len(aggregatedQubits[pointerSecondGateQubit+1])):
                        pointerTable[aggregatedQubits[pointerSecondGateQubit+1][k]] = pointerSecondGateQubit

                    aggregatedQubits[pointerSecondGateQubit] = aggregatedQubits[pointerSecondGateQubit+1]
                    aggregatedQubits[pointerSecondGateQubit+1] = []

                    gatesCovered[pointerSecondGateQubit] = gatesCovered[pointerSecondGateQubit+1]
                    gatesCovered[pointerSecondGateQubit+1] = []        

                    pointerSecondGateQubit += 1



                    if pointerSecondGateQubit >= len(aggregatedQubits)-1:
                        break
                



            '''
            At this point, the sets have been merged and sorted. Now, to evaluate how well the gates are covered by these particular sets. 
            '''        

                
            # Now that the qubit set as well as the gate coverage set are updatet, check the gate coverage
            # So: How many gates are covered by the Qubit sets S = [S_1, S_2, ...] ?

            gateCoverage, qubitNonCoverage = EvaluateGateCoverage(aggregatedQubits, gatesCovered, nQ, qMax, mMax)

            # termination condition: 
            # if the remaining qubits - those that can be covered by the constellation (excluding these that cannot be covered because they are more than Q) - are less than the qubits that can be stored in the processing zones 
            # in total, so mMax (no of processing zones) times qMax (no of qubits in processing zones)
            if nQ - qubitNonCoverage < mMax * qMax: 

                print('Termination condition reached!')
                # function returns the two best lists, because we're running out of space 
                return aggregatedQubitsBest, gatesCoveredBest, gateCoverageList
            


            gateCoverageList.append(gateCoverage)

            # store best gateCoverage
            if gateCoverage > bestGateCoverage: 
                bestGateCoverage = gateCoverage

                aggregatedQubitsBest    = aggregatedQubits.copy()
                gatesCoveredBest        = gatesCovered.copy()


    return aggregatedQubitsBest, gatesCoveredBest, gateCoverageList        
            


aggregatedQubitsTest, gatesCoveredBestTest, gateCoverageTest = AggregateBlocksStep(layeredCircuit, NQ, QMAX, MMAX)



# Plot the blockaggregation procedure  

# plt.figure()
# plt.title('Developement of the gatecoverage during blockaggregation \n')
# plt.plot(gateCoverageTest, label = 'gateCoverage')
# plt.legend()
# plt.ylabel('Gatecoverage')
# plt.xlabel('Iterations')
# plt.show()

def AggregateBlocksStepPostProcess(aggregatedQubits, gatesCovered, nQ, qMax, mMax):
    '''
    Given:
        S - A set of qubits in the processing zones 
        G - Set of gates covered by these qubits 
        nQ - Number of qubits 
        qMax -
        mMax - 
    Returns: 
        SP - Qubit sets in processing zones after padding with idle qubits 
        GP - Gates covered by these new qubit sets (does not change)
        Iset - A global pool of idle qubits that are not in processing zones  
        c - Updatet pointers for all the qubits 


    After the block aggregation step, this function does a couple of things: 
        1. It selects the sets to be used as processing zone sets 
        2. It pads these sets with additional idle qubits 
        3. It fills all the remaining qubits into a global Idle pool
        4. It builds a new structure of pointer variables for further processing 

    Each pointer variable to qubit q is now a quadruple: {s, m, k, s'}, where: 
        s = {'p', 'i'}:  indicates if q is stored in processing zone or idle pool 
        m = {0, ...}  processing zone number 
        k = {1, ...} position within processing zone or idle pool 
        s'= {'a', 'i'} active or idle (within processing zone, the qubits in idle pool are always idle / inactive.)

    '''

    # set of processing zone sets, SP
    qubitsInProcessingZones = []

    # set of covered gates corresponding to processing zone sets, GP 
    gatesCoveredProcessingZones = []

    pointerQuadruple = [[] for _ in range(nQ)]

    # Idle pool qubits
    idlePool = []

    # essentially a processing zone counter 
    processingZoneCtr = 0

    # iterate over the aggregated sets (processing blocks so far)
    for n in range(len(aggregatedQubits)):

        # if this particular set of qubits fits into the processing zone, append to processing zone sets and corresponding gate coverage set
        if len(aggregatedQubits[n]) <= qMax and processingZoneCtr <= mMax - 1: 
            qubitsInProcessingZones.append(aggregatedQubits[n])
            gatesCoveredProcessingZones.append(gatesCovered[n])

            # first position is zeroth position
            positionInZone = 0

            # assign pointers to the qubits in this set 
            for qi in range(len(aggregatedQubits[n])):
                q =  aggregatedQubits[n][qi]
                pointerQuadruple[q] = ['p', processingZoneCtr, positionInZone, 'a']
                positionInZone += 1 

            # now that this processing zone has been filled, focus on next one 
            processingZoneCtr += 1   

           
        # if the qubits do not fit into the processing zone, we add them to the idle pool!    
        else:
            idlePool = idlePool + aggregatedQubits[n]  

    # Pad processing zones with qubits from idle pool 
    for processingZone in range(mMax):

        # idle subset of processing zone 
        idleqQubitsInProcessingZones = []

        # if there is only one qubit in the m-th processing zone
        if len(qubitsInProcessingZones[processingZone]) == 1:

            # take this qubit 
            q = qubitsInProcessingZones[processingZone][0]

            # and empty this list 
            qubitsInProcessingZones[processingZone] = []

            # append this qubit to the idle subset of the processing zone m 
            idleqQubitsInProcessingZones = [q]

            # this qubit is now idle, but it is still in a processing zone, not a storage zone  
            pointerQuadruple[q] = ['p', processingZone, 0, 'i']
        
        # a qubit that is appended to a certain processing zone will have this position: 
        positionInZone = len(qubitsInProcessingZones[processingZone]) + len(idleqQubitsInProcessingZones)

        # while all qubits (active and idle) in the processing zone are less than the maximum possible number of qubits in the processing zone, 
        # we pad the processing zone with more idle qubits from the idle pool 
        while len(qubitsInProcessingZones[processingZone])+ len(idleqQubitsInProcessingZones) < qMax:

            # take the first qubit in the idle pool
            q = idlePool[0]

            # append the qubit from the idle pool to the idle subset of the processing zone 
            idleqQubitsInProcessingZones.append(q)

            # and adjust its pointer accordingly, it's idle, but now in a processing zone 
            pointerQuadruple[q] = ['p', processingZone, positionInZone, 'i']

            # erase this qubit from the idle pool - it was moved to the processing zone 
            idlePool = idlePool[1:]
            positionInZone += 1 
        
        # update the qubits in processing zone m 
        qubitsInProcessingZones[processingZone] = qubitsInProcessingZones[processingZone] + idleqQubitsInProcessingZones

    # end of for loop 

    # now, as a last step, assign the pointer variables for all qubits remaining in the global idle pool 
    for qubitIndex in range(len(idlePool)):
        qubitInIdlePool = idlePool[qubitIndex]

        # qubits are idle in idle pool, no processing zones in idle pool - number always 1
        pointerQuadruple[qubitInIdlePool] = ['i', 1, qubitIndex, 'i']


    return qubitsInProcessingZones, gatesCoveredProcessingZones, idlePool, pointerQuadruple



# test 
# SP, GP, Iset, c = AggregateBlocksStepPostProcess(aggregatedQubitsTest, gatesCoveredBestTest, NQ, QMAX, MMAX)

# print('SP:', SP)
# print('GP:', GP)

'''
Now, we have padded the processing zones with idle qubits, so the processing zones are now filled with active and idle qubits. 
We are done with the processing zones. 

Now, as one last step, we have to take the qubits from the idle pool and place them into storage zones in the processing blocks. 
'''


def PlaceIdlePoolQB(storageZoneShape, idlePool, pointerQuadruple):
    '''
    Given: 
        Fsizes, a list of sizes of storage zones. E.g. for two storages zones with size 10 each: Fsizes = [10,10]
        Iset: A pool of idle qubits that are not inside processing zones
        c: Pointer variables for the qubits in the idle pool
    Returns: 
        Fset, a set of storage zones filled with qubits 
        cnew: An updated pointer list for the idle qubits 

    this function places qubits from a global idle pool into idle storage zones with max capacities specified by F sizes 
    The qubits, in this version, are placed starting from the middle outwards. 
    '''

    # number of storage zones: 
    numF = len(storageZoneShape)

    # first storage zone to be filled up, remember: we're starting in the middle, keeping in mind the indexing by python
    storageZoneNumber = math.floor(numF / 2) - 1

    # initialize empty storage zones, list of empty lists
    storageZoneQubits = [[] for _ in range(numF)]

    # idle pool, create a copy that will be continuosly decreased 
    newIdlePool = idlePool
    
    # pointer table 
    newPointerQuadruple = pointerQuadruple

    # Now, to fill up these idle zones. We start in the starting zone, moving left and right, filling up the zones 
    # we go through the storage zones starting with a right zone, corresponding to fp, then a left zone, corresponding to fm 
    storageZone = storageZoneNumber
    nextStorageZone = storageZoneNumber+1 
    ctr = 1 

    # while there's still qubits left in the idle pool 
    while len(newIdlePool) > 0: 
        '''
        Right zone
        '''
        # if we are still within the allowed number of storage zones but the number of qubits in this storage zone is too high, move to the left 
        if nextStorageZone < numF and len(storageZoneQubits[nextStorageZone]) >= storageZoneShape[nextStorageZone]:
            nextStorageZone += 1

        # if we are within the allowed number of storage zones and the fp-th storage zone still needs to be filled 
        if nextStorageZone < numF and len(storageZoneQubits[nextStorageZone]) < storageZoneShape[nextStorageZone]:

                # take the first qubit in the idle pool 
                q = newIdlePool[0]

                # append this qubit to the storage zone 
                storageZoneQubits[nextStorageZone].append(q)

                # and adjust their pointer variables accordingly, where fp is the number of the storage zone
                newPointerQuadruple[q] = ['i', nextStorageZone, len(storageZoneQubits[nextStorageZone])-1, 'i']

                # eliminate qubit q from idle pool 
                newIdlePool = [x for x in newIdlePool if x != q]

        '''
        Left zone 
        '''
        # if within the allowed number of storage zones and the fm-th storage zone is too full 
        if storageZone > 0 and len(storageZoneQubits[storageZone]) >= storageZoneShape[storageZone]:
            storageZone -= 1
        
        # if the fm-th storage zone still has to be filled 
        if storageZone >= 0 and len(storageZoneQubits[storageZone]) < storageZoneShape[storageZone]:

            # take the first qubit in the idle pool 
            q = newIdlePool[0]

            # append this qubit to the storage zone 
            storageZoneQubits[storageZone].append(q)

            # and adjust their pointer variables accordingly 
            newPointerQuadruple[q] = ['i', storageZone, len(storageZoneQubits[storageZone])-1, 'i']

            # eliminate qubit q from idle pool 
            newIdlePool = [x for x in newIdlePool if x != q]


        # if all storage zones are filled up and there's qubits left in the idle pool, error 
        if nextStorageZone == numF-1 and len(storageZoneQubits[nextStorageZone-1]) >= storageZoneShape[nextStorageZone-1] and storageZone == 1 and len(storageZoneQubits[storageZone-1]) >= storageZoneShape[storageZone-1] and len(newIdlePool) > 0:
            print('ERROR: No more storage zones left, but not all qubits placed.')
            return storageZoneQubits, newPointerQuadruple

    return storageZoneQubits, newPointerQuadruple          




'''
Now, all subalgorithms have been taken care of.
We can implement the main algorithm 
'''


def blockProcessCircuit(rawCircuit, nQ, storageZoneShape, qMax, mMax):
    '''
    This is the Main function executing the Block aggregation algorithm step by step. 

    This function step by step removes gates from the given circuit rawCircuit, based on  

    Accepts: 
        rawCircuit: The raw Circuit, 
        nQ:         the number of Qubits in the circuit, 
        Fsizes:     The sizes of the processing zones 
        qMax:       The maximal number of Qubits that can be stored within a processing zone 
        mMax:       The number of processing zones within a processing block 

    Returns: 
        B:          List of aggregated processing blocks, arranged like: [[S, G, F, c], [....], ..., [S,G,F,c]] with len(B) = number of processing blocks 
        

    '''

    # Raw Circuit to be manipulated 
    rawCircuitChange = rawCircuit

    # list of aggregated blocks 
    aggregatedBlocks = []

    iterationCounter = 0

    # while stuff still left in circuit 
    while rawCircuitChange != [] and iterationCounter<100:


        # Make layeredcircuit
        tempLayeredCircuit                   = LayerCircuit(nQ, rawCircuitChange)


        # Get best set of qubits and gates from algorithm 
        aggregatedQubitsBest, gatesCoveredBest, gc_list_test      = AggregateBlocksStep(tempLayeredCircuit, nQ, qMax, mMax)


        # Get set of qubits and gates, for the different processing zones. And the 'remaining' idle pool Iset 
        processingZoneQubits, coveredGates, Iset, pointerQuadruple     = AggregateBlocksStepPostProcess(aggregatedQubitsBest, gatesCoveredBest, nQ, qMax, mMax)


        # Finally, fill storage zones with qubits in 'remaining' idle pool 
        storageZoneQubits, pointerQuadrupleNew            = PlaceIdlePoolQB(storageZoneShape, Iset, pointerQuadruple)

        # iterate over the different sets of gates in GP
        for gateNo in range(len(coveredGates)):

            rawCircuitChange = [rawCircuitChange[i] for i in range(len(rawCircuitChange)) if rawCircuitChange[i][0] not in coveredGates[gateNo]]

        
        # append this set of S, G, F and c to the collection of processing blocks 
        aggregatedBlocks.append([processingZoneQubits, coveredGates, storageZoneQubits, pointerQuadrupleNew])

        iterationCounter += 1

    return aggregatedBlocks


processingBlockArrangement = blockProcessCircuit(circuitOfQubits, NQ, FSIZES, QMAX, MMAX)



'''

DISPLAYING

'''

def visualize_blocks(B, title):
    '''
    Given a list B, this function plots the qubits in the corresponding processing blocks. Same qubits are connected to each other between neighbouring layers. 
    The visualization is done for an arbitrary number of qubits, arranged in arbitrarily sized processing and storage zones. 
    Only constraint:    All processing and storage zones have to be equal in size, respectively. 
                        And the system has to be arranged like: 

                        Storage zone
                        Processing zone
                        Storage zone
                        Processing zone 
                        ...
                        Storage zone

    Accepts: 
        B:          List of interest in optimization procedure 
        title:      A title for the plot 
    Returns: 
        Nothing 

    '''

    # extract c from B
    c_total = []
    for i in range(len(B)):
        c_total.append(B[i][3])

    # Graph 
    G = nx.Graph() 

    

    # add nodes for all the qubits in the different layers 
    # every qubit gets assigned a zone keyword indicating in what zone it is and a label keyword indicating what number qubit it is. Also a layer number indicating what layer it is in. 

    # iterate over blocks 
    for layerNumber in range(len(c_total)):

        # iterate over qubits in block 
        for qubitNumber in range(len(c_total[layerNumber])):

            # if in storage zone, add with corresponding label and zone keyword 
            if c_total[layerNumber][qubitNumber][0] == 'i':
                G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='storage', label=str(qubitNumber))

            # if in processing zone, add with corresponding label and zone keyword, remember: qbs can still be idle in processing zone, so we have to differentiate 
            elif c_total[layerNumber][qubitNumber][0] == 'p': 

                if c_total[layerNumber][qubitNumber][3] == 'i':
                    G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_idle', label=str(qubitNumber))

                elif c_total[layerNumber][qubitNumber][3] == 'a':
                    G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_active', label=str(qubitNumber))

    # assign positions to all the qubits 
    pos = {}

    lenProcessingZones =  len(B[0][0][0]) # corresponds to S list 
    print((B[0][0][0]))
    print(len(B[0][2][0]))
    # print(c_total[0])
    # print(c_total[0][2])
    lenStorageZones =  len(B[0][2][0]) # corresponds to F list 

    for node in G.nodes():

        # node is a tuple, node = (layer_number, node_number)
        layer_idx, node_idx = node
        
        # x position is just the layer number 
        x = layer_idx

        # depending if in storage, or processing zone, assign y coordinates 
        # storage zone 
        if c_total[layer_idx][node_idx][0] == 'i':
            y = c_total[layer_idx][node_idx][1]*- (lenStorageZones + lenProcessingZones) - c_total[layer_idx][node_idx][2]

        # processing zone 
        elif c_total[layer_idx][node_idx][0] == 'p':
            y = - lenStorageZones - (lenStorageZones + lenProcessingZones) *(c_total[layer_idx][node_idx][1]) - c_total[layer_idx][node_idx][2]

        # pos is a dictionary, pos((processingblock_number, qubit_number) = (x, y)). 
        # pos stores this for all the qubits in all the blocks 

        pos[node] = (x, y)


    # add edges 
    # We always add an edge between a qubit and the one in the layer next to it on the right. So, for the rightmost layer, we do not have to add an edge.
    for layerNumber in range(len(c_total)-1):
        for qubitNumber in range(len(c_total[layerNumber])):
            # current node is tuple
            current_node = (layerNumber, qubitNumber)

            # want to find the node in the layer next to it on the right that has the same label (corresponds to the same qubit)
            for qubitNumber_ in range(len(c_total[layerNumber+1])):

                # if we found the qubit with the same label 
                if G.nodes[current_node]['label'] == G.nodes[(layerNumber+1, qubitNumber_)]['label']:
                    next_node = (layerNumber + 1, qubitNumber_) 

                    # add an edge connecting these two nodes to the graph 
                    G.add_edge(current_node, next_node)

    # clarifying that the label keyword is actually the label that we want to use 
    node_labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    plt.figure(figsize=(10, 8))
    plt.title(title)
    nx.draw(G, pos, node_size=200, node_color=['red' if G.nodes[node]['zone'] == 'storage' else 'green' if G.nodes[node]['zone'] == 'processing_active' else 'blue' for node in G.nodes()], labels=node_labels, with_labels=True)
    
    # Add layer labels above nodes
    for layerNumber in range(len(c_total)):
        romanNumberList = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XII', 'XIII']
        layer_label = f'{romanNumberList[layerNumber]}'
        x = layerNumber
        y = max(pos[node][1] for node in pos if node[0] == layerNumber) + 0.7  # Adjust the y-coordinate for the label placement
        plt.text(x, y, layer_label, fontsize=12, ha='center', va='bottom')


    plt.show()    


# show arrangement of qubits after block aggregation
# visualize_blocks(processingBlockArrangement, 'Qubits arranged after block aggregation')


'''
ANIMATION
'''

def update(num, bList, title, ax):
    '''
    this function is used in the function animateSolving below
    Given a
    number of frames for the animation
    list of processingBlockArrangements - corresponding to certain swaps in the optimization algorithm procedure
    title
    and ax, a matplotlib object
    it creates the plot of the graph for every element in the processingBlockArrangementList 
    '''
    ax.clear()

    B = bList[num]
    
    if num < len(bList)-1:
        print('DEBUG: ', bList[num] == bList[num+1])

    # extract c from B
    c_total = []
    for i in range(len(B)):
        c_total.append(B[i][3])

    # Graph 
    G = nx.Graph() 

    

    # add nodes for all the qubits in the different layers 
    # every qubit gets assigned a zone keyword indicating in what zone it is and a label keyword indicating what number qubit it is. Also a layer number indicating what layer it is in. 

    # iterate over blocks 
    for layerNumber in range(len(c_total)):

        # iterate over qubits in block 
        for qubitNumber in range(len(c_total[layerNumber])):

            # if in storage zone, add with corresponding label and zone keyword 
            if c_total[layerNumber][qubitNumber][0] == 'i':
                G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='storage', label=str(qubitNumber))

            # if in storage zone, add with corresponding label and zone keyword, remember: qbs can still be idle in processing zone, so we have to differentiate 
            elif c_total[layerNumber][qubitNumber][0] == 'p': 

                if c_total[layerNumber][qubitNumber][3] == 'i':
                    G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_idle', label=str(qubitNumber))

                elif c_total[layerNumber][qubitNumber][3] == 'a':
                    G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_active', label=str(qubitNumber))


    # assign positions to all the qubits 
    pos = {}

    lenProcessingZones =  len(B[0][0][0]) # corresponds to S list 
    print((B[0][0][0]))
    print(len(B[0][2][0]))
    lenStorageZones =  len(B[0][2][0]) # corresponds to F list 

    for node in G.nodes():

        # node is a tuple, node = (layer_number, node_number)
        layer_idx, node_idx = node
        
        # x position is just the layer number 
        x = layer_idx

        # depending if in storage, or processing zone, assign y coordinates 
        # storage zone 
        if c_total[layer_idx][node_idx][0] == 'i':
            y = c_total[layer_idx][node_idx][1]*- (lenStorageZones + lenProcessingZones) - c_total[layer_idx][node_idx][2]

        # processing zone 
        elif c_total[layer_idx][node_idx][0] == 'p':
            y = - lenStorageZones - (lenStorageZones + lenProcessingZones) *(c_total[layer_idx][node_idx][1]) - c_total[layer_idx][node_idx][2]

        # pos is a dictionary, pos((processingblock_number, qubit_number) = (x, y)). 
        # pos stores this for all the qubits in all the blocks 

        pos[node] = (x, y)


    # add edges 
    # We always add an edge between a qubit and the one in the layer next to it on the right. So, for the rightmost layer, we do not have to add an edge.
    for layerNumber in range(len(c_total)-1):
        for qubitNumber in range(len(c_total[layerNumber])):
            # current node is tuple
            current_node = (layerNumber, qubitNumber)

            # want to find the node in the layer next to it on the right that has the same label (corresponds to the same qubit)
            for qubitNumber_ in range(len(c_total[layerNumber+1])):

                # if we found the qubit with the same label 
                if G.nodes[current_node]['label'] == G.nodes[(layerNumber+1, qubitNumber_)]['label']:
                    next_node = (layerNumber + 1, qubitNumber_) 

                    # add an edge connecting these two nodes to the graph 
                    G.add_edge(current_node, next_node)

    # clarifying that the label keyword is actually the label that we want to use 
    node_labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    # plt.figure(figsize=(10, 8))
    # plt.title(title)
    
    nx.draw(G, pos, node_size=200, node_color=['red' if G.nodes[node]['zone'] == 'storage' else 'green' if G.nodes[node]['zone'] == 'processing_active' else 'blue' for node in G.nodes()], labels=node_labels, with_labels=True)

    ax.set_title(title + ', iteration: ' + str(num))




def animate_solving(bList, title):
    fig, ax = plt.subplots(figsize=(10,8))

    ani = animation.FuncAnimation(fig, update, frames=len(bList), interval=100, repeat=False, fargs= (bList, title, ax))
    plt.show()





def show_circuit_after_optimizing(BP, nQ, circ):
    '''
    This function uses qiskit to display a circuit with nQ qubits. The gates are displayed as dictated by the circ list created in the function random_circuit. 
    '''
    q_a = QuantumRegister(nQ, name='q')
    circuit = QuantumCircuit(q_a)
    for step in range(len(BP)):

        for g in range(len(BP[step][1][0])):

            # gate = layeredcirc[i][g][0]
            gate = BP[step][1][0][g]
            # print('test', gate)

            # q1 = circ[i][g][1][0]
            q1 = circ[gate][1][0]
            q2 = circ[gate][1][1]
            # q2 = circ[i][g][1][1]

            # circuit.cz(q_a[circ[gate][1][0]-1], q_a[circ[gate][1][1]-1], label=str(g+1))
            circuit.cz(q1, q2, label=str(gate+1))


        circuit.barrier()
    circuit.draw(output='mpl', justify='none', fold = 50)
    plt.title("Circuit arranged in layers \n")
    plt.show()
    # print(circuit)

# show_circuit_after_optimizing(processingBlockArrangement, NQ, circuitOfQubits)
# visualize_blocks(B, 'Visualizing Test')



