import numpy as np
import matplotlib.pyplot as plt
import random
import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import math 

import matplotlib.animation as animation

import networkx as nx
from fancify_text import italic, bold, italicSerif
 
from HelperFunctions import *

from RandomCircuitQiskit import *

'''
In this file, the mathematica file ... 
will be transcripted into python, extended and commented in order for other people to be able to use it. 

There are a few important files involved in this project. 
The first one is randomcircuit.py - it creates a random circuit and plots it using qiskit. 


The third one is blockprocessing.py - it applies the block aggregation algorithm to the circuit. 

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

# circuitOfQubits, listOfGateMatrices = CreateRandomCircuit(NQ, GATES, 2, False)
# commutationMatrix = GetCommutationMatrix(listOfGateMatrices)
# AllowedArrangements = GetAllValidCircuits(gatesList, commutationMatrix)

# gatesList, commutationMatrix = CreateRandomCircuit(NQ, GATES, 2, display= False)
# possibleArrangements = BFS([gatesList], commutationMatrix)
# Here, and this is important to understand, AllowedArrangements is a list of allowed circuit arrangements (due to gates being able to commute with each other)



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




def AggregateBlocksStep(circuitOfQubits, nQ, qMax, mMax):
    '''
    The goal is to find the set of S and G that produce the best GateCoverage!!

    Given: 
        circuitOfQubits:    A circuit
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
    for gateNo in range(len(circuitOfQubits)):

        gate = circuitOfQubits[gateNo]
        
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

            # debug print statement
            # print('Termination condition reached!')
            # function returns the two best lists, because we're running out of space 
            return aggregatedQubitsBest, gatesCoveredBest, gateCoverageList, bestGateCoverage
        


        gateCoverageList.append(gateCoverage)

        # store best gateCoverage
        if gateCoverage > bestGateCoverage: 
            bestGateCoverage = gateCoverage

            aggregatedQubitsBest    = aggregatedQubits.copy()
            gatesCoveredBest        = gatesCovered.copy()

        # print(aggregatedQubits)


    return aggregatedQubitsBest, gatesCoveredBest, gateCoverageList, bestGateCoverage      
            

# print(circuitOfQubits)
# aggregatedQubitsTest, gatesCoveredBestTest, gateCoverageTest = AggregateBlocksStep(circuitOfQubits, NQ, QMAX, MMAX)
# print('Best:')
# print(aggregatedQubitsTest)
# print(aggregatedQubitsTest)

# print(circuitOfQubits)

# exit()
# print(aggregatedQubitsTest)

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
        c - Updated pointers for all the qubits 


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

            # take random qubit from idle pool 
            randomQubitNo = random.randint(0, len(idlePool) - 1)

            idleQubit = idlePool.pop(randomQubitNo)

            # append the qubit from the idle pool to the idle subset of the processing zone 
            idleqQubitsInProcessingZones.append(idleQubit)

            # and adjust its pointer accordingly, it's idle, but now in a processing zone 
            pointerQuadruple[idleQubit] = ['p', processingZone, positionInZone, 'i']

            # erase this qubit from the idle pool - it was moved to the processing zone 
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


def PlaceIdlePoolQB(storageZoneShape, idlePool, pointerQuadruple, randomPlacement = False):
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
    numberOfStorageZones = len(storageZoneShape)

    # first storage zone to be filled up, remember: we're starting in the middle, keeping in mind the indexing by python
    storageZoneNumber = math.floor(numberOfStorageZones / 2) - 1

    # initialize empty storage zones, list of empty lists
    storageZoneQubits = [[] for _ in range(numberOfStorageZones)]

    # 
    # COULD BE NUMPY!!!
    # 


    # idle pool, create a copy that will be continuosly decreased 
    newIdlePool = idlePool
    
    # pointer table 
    newPointerQuadruple = pointerQuadruple

    # Now, to fill up these idle zones. We start in the starting zone, moving left and right, filling up the zones 
    # we go through the storage zones starting with a right zone, corresponding to fp, then a left zone, corresponding to fm 

    # initialize the storage zone number to the middle storage zone!
    storageZone = storageZoneNumber
    nextStorageZone = storageZoneNumber+1 


    # while there's still qubits left in the idle pool 
    while len(newIdlePool) > 0: 

        '''
        Right zone
        '''

        # if (the right partner of the current) storage zone is still within the allowed number of storage zones but the number 
        # of qubits in this storage zone is maximal, move to the right! (down) 
        if nextStorageZone < numberOfStorageZones and len(storageZoneQubits[nextStorageZone]) >= storageZoneShape[nextStorageZone]:
            nextStorageZone += 1

        # if we are within the allowed number of storage zones and the current right partner storage zone is not filled yet, fill it!
        if nextStorageZone < numberOfStorageZones and len(storageZoneQubits[nextStorageZone]) < storageZoneShape[nextStorageZone]:

                # if random
                if randomPlacement: 
                    # choose random qubit from the idle pool 
                    randomQubitNo = random.randint(0, len(newIdlePool) - 1)

                    # eliminate this qubit from the idle pool 
                    randomIdleQubit = newIdlePool.pop(randomQubitNo)

                # if not random
                else: 
                    # take the first qubit in the idle pool 
                    randomIdleQubit = newIdlePool[0]

                    # eliminate qubit q from idle pool 
                    newIdlePool = [x for x in newIdlePool if x != randomIdleQubit]

                # append this qubit to the (right partner of the current) storage zone 
                storageZoneQubits[nextStorageZone].append(randomIdleQubit)

                # and adjust their pointer variables accordingly
                newPointerQuadruple[randomIdleQubit] = ['i', nextStorageZone, len(storageZoneQubits[nextStorageZone])-1, 'i']



        '''
        Left zone 
        '''

        # now, look at the original storage zone (*not* its partner on the right)

        # if the current storage zone is not the leftmost one and is completely filled, move to the left 
        if storageZone > 0 and len(storageZoneQubits[storageZone]) >= storageZoneShape[storageZone]:
            storageZone -= 1
        
        # if the currrent storage zone is *not* full yet
        if storageZone >= 0 and len(storageZoneQubits[storageZone]) < storageZoneShape[storageZone]:


            # if random
            if randomPlacement: 

                # choose a random qubit from the idle pool 
                randomQubitNo = random.randint(0, len(newIdlePool) - 1)

                # eliminate this random qubit from the idle pool 
                randomIdleQubit = newIdlePool.pop(randomQubitNo)

            # if not random
            else: 
                # take the first qubit in the idle pool 
                randomIdleQubit = newIdlePool[0]

                # eliminate qubit q from idle pool 
                newIdlePool = [x for x in newIdlePool if x != randomIdleQubit]

            # append this qubit to the current storage zone 
            storageZoneQubits[storageZone].append(randomIdleQubit)

            # and adjust their pointer variables accordingly 
            newPointerQuadruple[randomIdleQubit] = ['i', storageZone, len(storageZoneQubits[storageZone])-1, 'i']




        # if all storage zones are filled up and there's qubits left in the idle pool, error 
        if nextStorageZone == numberOfStorageZones-1 and len(storageZoneQubits[nextStorageZone-1]) >= storageZoneShape[nextStorageZone-1] and storageZone == 1 and len(storageZoneQubits[storageZone-1]) >= storageZoneShape[storageZone-1] and len(newIdlePool) > 0:
            print('ERROR: No more storage zones left, but not all qubits placed.')
            return None

    return storageZoneQubits, newPointerQuadruple          





def DetermineBestArrangement(possibleArrangementsList, nQ, qMax, mMax): 
    '''
    This is a function that calculates, given a number of possible arrangements of the gates in the circuit, the one with the highest gate coverage 
    '''
    bestGateCoverageList = []
    for circuitNo in range(len(possibleArrangementsList)): 
        circuit = possibleArrangementsList[circuitNo]
        a, b, c, bestGateCoverage      = AggregateBlocksStep(circuit, nQ, qMax, mMax)
        bestGateCoverageList.append(bestGateCoverage)
    
    # choose circuit with best gateCoverage 
    bestCircuit = possibleArrangementsList[bestGateCoverageList.index(max(bestGateCoverageList))]

    return bestCircuit 


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


    # while stuff still left in circuit 
    while rawCircuitChange != []:

    
        # Get best set of qubits and gates from algorithm 
        aggregatedQubitsBest, gatesCoveredBest, gc_list_test, bestGateCoverage      = AggregateBlocksStep(rawCircuitChange, nQ, qMax, mMax)


        # Get set of qubits and gates, for the different processing zones. And the 'remaining' idle pool Iset 
        processingZoneQubits, coveredGates, Iset, pointerQuadruple     = AggregateBlocksStepPostProcess(aggregatedQubitsBest, gatesCoveredBest, nQ, qMax, mMax)


        # Finally, fill storage zones with qubits in 'remaining' idle pool 
        storageZoneQubits, pointerQuadrupleNew            = PlaceIdlePoolQB(storageZoneShape, Iset, pointerQuadruple)

        # iterate over the different sets of gates in GP
        for gateNo in range(len(coveredGates)):

            rawCircuitChange = [rawCircuitChange[i] for i in range(len(rawCircuitChange)) if rawCircuitChange[i][0] not in coveredGates[gateNo]]

        
        # append this set of S, G, F and c to the collection of processing blocks 
        aggregatedBlocks.append([processingZoneQubits, coveredGates, storageZoneQubits, pointerQuadrupleNew])


    return aggregatedBlocks

# processingBlockArrangement = blockProcessCircuit(possibleArrangements, NQ, FSIZES, QMAX, MMAX)
# processingBlockArrangement2 = blockProcessCircuit(circuitOfQubits, NQ, FSIZES, QMAX, MMAX)


# visualize_blocks(processingBlockArrangement, 'Arrangement after Block Aggregation')
# visualize_blocks(processingBlockArrangement2, 'Arrangement after Block Aggregation')