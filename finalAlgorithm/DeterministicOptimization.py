import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import copy 
from BlockAggregation import *
from HelperFunctions import *


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
'''



# processingBlockArrangement = blockProcessCircuit(circuitOfQubits, NQ, FSIZES, QMAX, MMAX)


def improvePlacement(processingBlockArrangement, nQ, storageZoneSizes, maxProcessingZoneQubits, numberProcessingZones, echo):
    '''
    This function improves the placement of the qubits, subsequently minimizing the metric used in the function 
    computeTotalCost()
    this function will be referred to as the deterministic part of the optimization procedure. 
    
    It just iterates over all the qubits and their possible swapping partners and checks if a global cost metric is minimized upon each swap. 

    Given: 
    processingBlockArrangement:     a list of Blocks and their corresponding variables S, G, c, 
    nQ:     Number of total qubits
    storageZoneSizes: Sizes of the storage zones 
    maxProcessingZoneQubits:   Maximum amount of qubits in processing zones 
    numberProcessingZones:   Number of processing zones in processing block 
    echo:   Do we want to print (debugging reasons)

    Returns: 
        newprocessingBlockArrangement: Updated list newprocessingBlockArrangement of qubits in processing blocks 
        List of total rearrangemet cost per iteration for displaying reasons


    '''

    # firstly, define variables of interest

    # list of Y positions of qubits for all the processing blocks, shape: shape(Y) = (num_processing_blocks, num_qubits)
    yPositionList = computeArrangements(processingBlockArrangement, storageZoneSizes, maxProcessingZoneQubits)

    # total cost to start with (of the initial qubit constellation)
    costTot = computeTotalCost(yPositionList, nQ)

    # number of processing blocks
    numberProcessingBlocks = len(processingBlockArrangement)

    # number of storage zones 
    numberStorageZones = len(storageZoneSizes)

    # for nested lists, this has to be done in python. copy() does not work for nested lists 
    newprocessingBlockArrangement = copy.deepcopy(processingBlockArrangement)

    '''
    There are different types of swaps that can be done. Of course, we cannot swap active qubits from a processing zone with qubits in storage zones. 
    
    at every iteration, we safe the best processingBlockArrangement so far, as well as the totcost. In the mathematica file, the expressions:
        Sow[costTot, 1];
        Sow[processingBlockArrangementnew, 2];
    safe these values for every iteration corresponding to the index 1 and 2. The reap and sow in the original file is only done for displaying reasons. 

    this function is split into four parts: 
        1. swap idle qubits between differennt idle ones to prevent crossings. 
        2. Swap idle qubits within idle zones to minimize the number of swaps possible in experiment 
        3. Swap whole processing zones 
        4. Swap qubitts within processing zones to minimize number of swaps needed. 


    Note that it doesn't make any sense to swap whole storage zones, because we can freely swap qubits between the storage zones. 
    '''

    processingBlockArrangementDisplaying = []

    # Iterate over the processing blocks
    for processingBlock in range(numberProcessingBlocks):


        # in the first processing block, we do not swap anything. It is only the relations *between* the processing blocks that count
        # since we always swap between a block and its left partner as well! 
        if processingBlock == 0: 
            continue 

        # get information from previous step to compare to current step
        previousProcessingZoneQubits, previousCoveredGates, previousStorageZoneQubits, previousPointerQuadruple = newprocessingBlockArrangement[processingBlock-1]

        # if we have not reached the end of the blocks yet, also define the right partner
        if processingBlock < numberProcessingBlocks-1:

            # variables for the processing block on the right 
            nextProcessingZoneQubits, nextCoveredGates, nextStorageZoneQubits, nextPointerQuadruple = newprocessingBlockArrangement[processingBlock+1]
        


        


        '''
        1. swap idle qubits between storage zones
        '''

        if echo == True:
            print('Swap idle qubits between storage zones ')

        # iterate over all the storage zones in the current processing block 
        for storageZone in range(numberStorageZones):

            processingZoneQubits, coveredGates, storageZoneQubits, pointerQuadruple = newprocessingBlockArrangement[processingBlock]

           

            # For all the qubits, we look at them in the processing blocks left and right to it. Why? 
            # To determine if it makes sense to swap them with other qubits in other storage zones 

            # We want to swap qubits q1 and q2 in the current block. 
            # Therefore, we examine a couple of things of q1 and q2 in the previous and next steps 

            # iterate over all idle qubits in the current storage zone 
            for qubitNo in range(len(storageZoneQubits[storageZone])):

                # qubit qubitNo in this storage zone 
                qubitOneInStorageZone = storageZoneQubits[storageZone][qubitNo]

                # processing/storage zone number of q1 in the previous block! 
                previousStorageZone = previousPointerQuadruple[qubitOneInStorageZone][1]

                # is q1 in idle or in processing block in previous step? 
                previousNatureStatus = previousPointerQuadruple[qubitOneInStorageZone][0]

                # processing zone number and zone indicator for qubit in the right processing block 
                if processingBlock < numberProcessingBlocks-1:
                    nextZoneNumberOne =  nextPointerQuadruple[qubitOneInStorageZone][1]
                    nextZoneStatusOne = nextPointerQuadruple[qubitOneInStorageZone][0]

                    # WE DO NOT!! ADD THIS, BECAUSE WE GO FROM LEFT TO RIGHT, WE COMPARE THE CURRENT TO THE LEFT NEIGHBOUR, AND NOT TO THE RIGHT AND THE LEFT 
                    # THIS WOULD BE TOO MUCH TO ASK FOR 

                    # if nextZoneStatusOne != 'i' or nextZoneNumberOne == storageZone: 
                    #     continue

                # if previous qubit is not idle, or the qubit in the previous processing block is in the same storage zone as the qubit in this processing block 
                # this is because we only want to swap the qubit to a position where it is in the same zone as in the previous step 
                # if it is not idle, we cannot do this, if it is in the same storage zone already, we're happy. 
                if previousNatureStatus != 'i' or previousStorageZone == storageZone:
                    continue



                # iterate over all storage zone qubits of this block in the storage zone, in which the qubit sits in in the previous step 
                for qubitIndex2 in range(len(storageZoneQubits[previousStorageZone])):

                    # qubit two, the qubit we want to exchange qubit 1 with 
                    qubitTwoInStorageZone = storageZoneQubits[previousStorageZone][qubitIndex2]

                    # we cannot swap a qubit with itself - this step is not necessary
                    # if qubitTwoInStorageZone == qubitOneInStorageZone: 
                    #     continue 
                    
                    # Processing/storage zone number of qubit 2 in previous step 
                    previousZoneTwo = previousPointerQuadruple[qubitTwoInStorageZone][1]

                    # Is qubit 2 which -again- sits in a different storage zone in the *current* blcok 
                    # is in idle or in processing zone in previous step?
                    previousZoneTwoNature = previousPointerQuadruple[qubitTwoInStorageZone][0]

                    # if we have not reached the rightmost layer, define z and s for the right neighbour (next step) as well 
                    if processingBlock < numberProcessingBlocks-1:

                        # processing zone number and indication in which kind of zone for qubit 2 in next step 
                        nextZoneNumberTwo = nextPointerQuadruple[qubitTwoInStorageZone][1]
                        nextZoneStatusTwo = nextPointerQuadruple[qubitTwoInStorageZone][0]

                    # if qubit one and qubit two are in the same zone in the previous step, continue, we do not want to swap them in this step
                    # ( remember: The zonenumber can be the same *although* the zonenature is not!! 
                    # Being in processing zone 2 or in storage zone 2 is different!! ) 
                    if previousZoneTwo == previousStorageZone and previousZoneTwoNature == 'i':
                        continue

                    # if, in the next step, q1 and q2 are in the same storage zone, continue 
                    if processingBlock < numberProcessingBlocks-1: 
                        if nextZoneNumberTwo == nextZoneNumberOne and nextZoneStatusTwo == 'i':
                            continue
                    

                    '''
                    swap qubit one and two in newprocessingBlockArrangement and in the Y list 
                    '''

                    q_temp = qubitOneInStorageZone
                    q2_temp = qubitTwoInStorageZone
                    # 1. Swap values in the sublist at the 4th position of processingBlockArrangementnew, corresponding to c 
                    newprocessingBlockArrangement[processingBlock][3][qubitOneInStorageZone], newprocessingBlockArrangement[processingBlock][3][qubitTwoInStorageZone] = pointerQuadruple[qubitTwoInStorageZone], pointerQuadruple[qubitOneInStorageZone]

                    # 2. Swap qubit indices in the sublist at the 3rd position of processingBlockArrangementnew for 'z'
                    newprocessingBlockArrangement[processingBlock][2][storageZone] = [q2_temp if x == q_temp else x for x in newprocessingBlockArrangement[processingBlock][2][storageZone]]

                    # 3. Swap qubit indices in the sublist at the 3rd position of processingBlockArrangementnew for 'zp'
                    newprocessingBlockArrangement[processingBlock][2][previousStorageZone] = [q_temp if x == q2_temp else x for x in newprocessingBlockArrangement[processingBlock][2][previousStorageZone]]


                    # swap q1 and q2 in Y and update the costTot
                    costTot, yPositionList[processingBlock] = updateStep(yPositionList, processingBlock, q_temp, q2_temp, costTot)


                    processingBlockArrangementDisplaying.append(copy.deepcopy(newprocessingBlockArrangement))

                    # break, because we're not going to swap anymore. 
                    # This is all the swapping we were interested in for 1)
                    break 

        # del processingZoneQubits, coveredGates, storageZoneQubits, pointerQuadruple

        
        '''
        2.  Swap idle qubits within idle zones to minimize swaps 
            Here, we have to keep in mind the position of the qubits *in* the processing zones. As opposed to above, where the only requirement was for the qubit to be in different processing zones over the blocks 
        '''

        if echo == True: 
            print('Swap idle qubits within storage zones')

        # iterate - again - over the storageZones in the current Block
        for storageZone in range(numberStorageZones):

            # THIS step!
            processingZoneQubits, coveredGates, storageZoneQubits, pointerQuadruple = newprocessingBlockArrangement[processingBlock]

            # iterate over all idle qubits 
            for qubitNo in range(len(storageZoneQubits[storageZone])):

                # qubit qubitNo in the z-th storage zone, up until here everyting is the same as above
                qubit1 = storageZoneQubits[storageZone][qubitNo]

                # Now different: We have to take into account the position in the storage zone 
                positionInZoneQubitOne = pointerQuadruple[qubit1][2]

                # processing zone number of previous block, qubit one 
                previousZoneNumberQubitOne = previousPointerQuadruple[qubit1][1]

                # is qubit one previously in idle or in processing zone? 
                previousZoneStatusQubitOne = previousPointerQuadruple[qubit1][0]

                # What position does qubit one have in the previous step in a storage zone? 
                previousPositionInZoneQubitOne = previousPointerQuadruple[qubit1][2]


                # if the qubit was in a different zone in the block before, it does not make sense to swap this qubit inside the current Zone! 
                # checking if it was idle in the step before amounts to - remember - just making sure that it was a storage zone in the step before 
                # because as far as numbering of the zones, there's no difference fot processing and storage zones 
                if previousZoneStatusQubitOne != 'i' or previousZoneNumberQubitOne != storageZone:
                    continue


                # iterate over all qubits in the *same* storage zone as possible swap partners (zp is now z)
                for qubitNo2 in range(len(storageZoneQubits[storageZone])):

                    # well, here it makes sense that we encounter q1 again
                    if qubitNo == qubitNo2: 
                        continue

                    # swap partner for q1
                    qubit2 = storageZoneQubits[storageZone][qubitNo2]

                    # we still cannot exchange the same qubit with itself
                    # this should be senseless
                    # if qubit2 == qubit1: 
                    #     continue 

                    # previous processing zone number of qubit 2 
                    previousZoneNumberQubitTwo = previousPointerQuadruple[qubit2][1]

                    # was qubit two in processing or storage zone in previous step? 
                    previousZoneStatusTwo = previousPointerQuadruple[qubit2][0]


                    # if, in previous step, q1 and q2 were not in the same storage zone, continue
                    # it only makes sense to swap two qubits that were inside the same storage zone in the block before as well! 
                    if previousZoneNumberQubitTwo != previousZoneNumberQubitOne or previousZoneStatusTwo != 'i':
                        continue

                    # position for qubit two 
                    positionInZoneQubitTwo = pointerQuadruple[qubit2][2]

                    # previous position for qubit two 
                    previousPositionInZoneQubitTwo = previousPointerQuadruple[qubit2][2]

                    # we now calculate if it makes sense to swap. In this case, it is not clear that it makes sense to swap. 
                    # in the case above, it was clear that the cost would be improved upon swapping. Here, there is situations where swapping 
                    # actually increases the cost! 

                    # compute a distance: 
                    # distance from qubit 1 in previous step to qubit one in this step 
                    # and distance from qubit 2 in previous and this step 
                    distance = (positionInZoneQubitOne-previousPositionInZoneQubitOne)**2 + (positionInZoneQubitTwo-previousPositionInZoneQubitTwo)**2

                    # And then: 
                    # Distance between q1 in this step and q2 in previous step 
                    # and distance between q2 in this and q1 in previous step 
                    distanceAfterSwapping = (positionInZoneQubitOne-previousPositionInZoneQubitTwo)**2 + (positionInZoneQubitTwo-previousPositionInZoneQubitOne)**2

                    # if the distance for the swapped case of q1 and q2 is bigger or equal to dist, continue 
                    if not distanceAfterSwapping < distance:
                        continue

                    # SWAPPING  

                    # important, because apparently, when newprocessingBlockArrangement gets altered, so does the corresponding c sublist... 
                    temporaryPointerQuadruple = pointerQuadruple[qubit1].copy()
                    newprocessingBlockArrangement[processingBlock][3][qubit1] = pointerQuadruple[qubit2]
                    newprocessingBlockArrangement[processingBlock][3][qubit2] = temporaryPointerQuadruple # c[q1] 

                    # swap qubits in storage zones (B = [[SP, GP, FP, c], ..., []]), so third element in B 
                    temporaryQubitOne = qubit1
                    temporaryQubitTwo = qubit2
                    newprocessingBlockArrangement[processingBlock][2][storageZone][qubitNo] = temporaryQubitTwo
                    newprocessingBlockArrangement[processingBlock][2][storageZone][qubitNo2] = temporaryQubitOne
                    
                    # update total cost and swap qubits in Y list 
                    costTot, yPositionList[processingBlock] = updateStep(yPositionList, processingBlock, temporaryQubitOne, temporaryQubitTwo, costTot)

                    # for the animation 
                    processingBlockArrangementDisplaying.append(copy.deepcopy(newprocessingBlockArrangement))

                    break 



        '''
        3. Swap entire processing zones to minimize swaps 
        '''

        if echo == True: 
            print('Swap entire processing zones')

        # as opposed to numberStorageZones, the number of storage zones, we now iterate over the processing zones 
        # -> z is processing zone number 
        for processingZone in range(numberProcessingZones):

            # small comment: when there's only one processing zone, this step obviously does not make any sense and is skipped 
            if numberProcessingZones == 1:
                continue


            # this is defined *in* the for loop since newprocessingBlockArrangement alters during the course of the for loop
            processingZoneQubits, coveredGates, storageZoneQubits, pointerQuadruple = newprocessingBlockArrangement[processingBlock]

            # The list of interest is now SP, which contains the qubits in the processing zones #
            # in the easiest case, we only have one processing zone which means: SP = [[q1,q2,q3,q4,q5]] with five qubits 
            # SPz is now the list of qubits in the z-th processing zone 
            qubitsInOneProcessingZone = processingZoneQubits[processingZone]


            # iterate over all processing zones, in order to swap processing zone with processing zone 
            for processingZoneTwo in range(numberProcessingZones):

                # not possible to swap the same processing zones 
                if processingZone == processingZoneTwo: 
                    continue
                

                # list of qubits in the second processing zone 
                qubitsInOneProcessingZoneTwo = processingZoneQubits[processingZoneTwo]

                # in mathematica, this is one expression, using np probably too 
                distance = 0
                # iterate over all the qubits in the processing zones 
                for qubitNo in range(maxProcessingZoneQubits):

                    # compute distance from the previous layers position of qubit 1 and 2 for all the qubits 
                    distance += ( yPositionList[processingBlock][qubitsInOneProcessingZone[qubitNo]] - yPositionList[processingBlock-1][qubitsInOneProcessingZone[qubitNo]] )**2 + ( yPositionList[processingBlock][qubitsInOneProcessingZoneTwo[qubitNo]] - yPositionList[processingBlock-1][qubitsInOneProcessingZoneTwo[qubitNo]] )**2

                # now, the same for distswap
                distanceAfterSwapping = 0
                for qubitNo in range(maxProcessingZoneQubits):

                    # if we were to swap, how would the distances look like? 
                    distanceAfterSwapping += ( yPositionList[processingBlock][qubitsInOneProcessingZoneTwo[qubitNo]] - yPositionList[processingBlock-1][qubitsInOneProcessingZone[qubitNo]] )**2 + ( yPositionList[processingBlock][qubitsInOneProcessingZone[qubitNo]] - yPositionList[processingBlock-1][qubitsInOneProcessingZoneTwo[qubitNo]] )**2
                
                # if swapping actually decreases the distance 
                if distanceAfterSwapping < distance:
                    # the two processing zones are swapped 
                    # first, in the list newprocessingBlockArrangement, so essentially we swap the elements in the SP list 


                    temp_b = newprocessingBlockArrangement[processingBlock][0][processingZone].copy()
                    newprocessingBlockArrangement[processingBlock][0][processingZone] = newprocessingBlockArrangement[processingBlock][0][processingZoneTwo]
                    newprocessingBlockArrangement[processingBlock][0][processingZoneTwo] = temp_b
                    # c[1], so the processing zone number is changed as well. That's all that changes for the qubits 
                    for qubitNo in range(maxProcessingZoneQubits):
                        
                        
                        # c[qi-th qubit in the z-th processing zone][1], the '1' indicates that we want to change the processing zone number 
                        newprocessingBlockArrangement[processingBlock][3][qubitsInOneProcessingZone[qubitNo]][1] = processingZoneTwo
                        newprocessingBlockArrangement[processingBlock][3][qubitsInOneProcessingZoneTwo[qubitNo]][1] = processingZone
                        # we have to do this in the for loop, because we can always only swap two qubits, not a set of qubits - maybe np.vectorize at some point 
                        costTot, yPositionList[processingBlock] = updateStep(yPositionList, processingBlock, qubitsInOneProcessingZone[qubitNo], qubitsInOneProcessingZoneTwo[qubitNo], costTot)

                    processingBlockArrangementDisplaying.append(copy.deepcopy(newprocessingBlockArrangement))

                    break

            

        '''
        4.  Swap qubits within processing zones to minimize swaps
            Swapping qubits in between processing zones does not make any sense obviously, since the corresponding gates do not commute 
        '''

        if echo == True: 
            print('Swap qubits within processing zones')


        # again, iterate over processing zones 
        for processingZone in range(numberProcessingZones):


            processingZoneQubits, gatesCovered, storageZoneQubits, pointerQuadruple = newprocessingBlockArrangement[processingBlock]
            
            # list of qubits in current processing zone 
            qubitsInOneProcessingZone = processingZoneQubits[processingZone]


            # iterate over all qubits in current processing zone 
            for qubitIndex in range(maxProcessingZoneQubits):

                # i-th qubit in z-th processing zone 
                qubitOne = qubitsInOneProcessingZone[qubitIndex]

                # position of q1 in processing zone 
                positionInZoneQubitOne = pointerQuadruple[qubitOne][2]

                # previous processing zone of qubit 
                previousZoneNumberQubitOne = previousPointerQuadruple[qubitOne][1]

                # previous zone of qubit 
                previousZoneStatusQubitOne = previousPointerQuadruple[qubitOne][0]

                # previous position in zone of qubit 
                previousPositionInZoneQubitOne = previousPointerQuadruple[qubitOne][2]

                # if this qubit was not in a processing zone in the previous step, or the processing zone numbers between this and previous step did not change, no need to switch this qubit #
                # we would then first have to switch the processing zones anyway I guess 
                if previousZoneStatusQubitOne != 'p' or previousZoneNumberQubitOne != processingZone:
                    continue 

                # iterate over all qubits in the same processing zone 
                for qubitIndexTwo in range(len(qubitsInOneProcessingZone)):

                    # if the indices qi and qi2 are the same, it means that they are in the same position in their processing zones. Thus, exchanging them does not make any sense. 
                    if qubitIndex == qubitIndexTwo: 
                        continue

                    # qubit 2 to be swapped with qubit 1 
                    qubitTwo = qubitsInOneProcessingZone[qubitIndexTwo]

                    # this is somehow different to the one above 
                    if qubitTwo == qubitOne: 
                        continue

                    # in what kinda zone? Has to be 'p'
                    previousZoneStatusTwo = previousPointerQuadruple[qubitTwo][0]

                    # processing zone number
                    previousZoneNumberQubitTwo  = previousPointerQuadruple[qubitTwo][1]

                    # if processing zone number of q1 is not the same as processing zone number of q2 in previous step, continue. Same as above 
                    if previousZoneStatusTwo != 'p' or previousZoneNumberQubitTwo != processingZone: 
                        continue 

                    # position of q2 in this step 
                    positionInZoneQubitTwo = pointerQuadruple[qubitTwo][2]

                    # position of q2 in previous step 
                    previousPositionInZoneQubitTwo = previousPointerQuadruple[qubitTwo][2]

                    # look at qubit one and two and their respective differences to the previous layers 
                    distance = (positionInZoneQubitOne-previousPositionInZoneQubitOne)**2 + (positionInZoneQubitTwo-previousPositionInZoneQubitTwo)**2

                    # and here in case of a swap 
                    distanceAfterSwapping = (positionInZoneQubitOne-previousPositionInZoneQubitTwo)**2 + (positionInZoneQubitTwo-previousPositionInZoneQubitOne)**2

                    # not important 
                    if echo == True: 
                        print(" candidates - z: ", processingZone, " zprev: ", previousZoneNumberQubitOne, " z2prev: ", previousZoneNumberQubitTwo, " q: ", qubitOne, " q2: ", qubitTwo)


                    # if we cant improve, just keep going 
                    if not (distanceAfterSwapping < distance):
                        continue


                    if echo == True:
                        print("  swap found - dist: ", distance, " distSwap: ", distanceAfterSwapping)


                    # all that is exchanged between those two qubits is the position inside the processing zone. This is the only part of the pointerlist c that we have to update 

                    newprocessingBlockArrangement[processingBlock][3][qubitOne][2] = positionInZoneQubitTwo
                    newprocessingBlockArrangement[processingBlock][3][qubitTwo][2] = positionInZoneQubitOne


                    costTot, yPositionList[processingBlock] = updateStep(yPositionList, processingBlock, qubitOne, qubitTwo, costTot)

                    processingBlockArrangementDisplaying.append(copy.deepcopy(newprocessingBlockArrangement))

                    # break has to be here, I put it one to the right and it did not work. Obviously. It just kept exchanging already exchanged qubits. 
                    # So: After one qubit exchange, we don't want to further exchange and break! 
                    break 


        '''
        Exchanging *all* possible idle qubits with each other. We are just interested in the idle qubit having an idle nature, it does not have to sit in a storage zone
        '''
        # for qubitNo in range(nQ): 



    # here, more parameters are returned in the future, for debugging and displaying reaasons 
    return newprocessingBlockArrangement, processingBlockArrangementDisplaying    



# processingBlockArrangementAfterOptimizing, bList = improvePlacement(processingBlockArrangement, NQ, FSIZES, QMAX, MMAX, True)


# animate_solving(bList, 'animation_test')
# visualize_blocks(processingBlockArrangementAfterOptimizing, 'Processing block arrangement after deterministic optimization, cost: ' + str(computeTotalCost(computeArrangements(processingBlockArrangementAfterOptimizing, FSIZES, MMAX), NQ)))
# # and before optimizing
# visualize_blocks(processingBlockArrangement, 'Processing block arrangement before optimization, cost: ' + str(computeTotalCost(computeArrangements(B, Fsizes, maxProcessingZoneQubits), nQ)))


