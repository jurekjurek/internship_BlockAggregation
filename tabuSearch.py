import numpy as np
import matplotlib.pyplot as plt
# import random 
import itertools 
from optimizing import *
from helperFunctions import *


'''
We can now update a B list given an old B list and a 'new' Y list that has been created by the tabu search. 
Now for the actual tabu search. 
'''


def improvePlacementTabuSearch(processingBlockArrangement, Fsizes, qMax, mMax, nQ, TSiterations, tabuListLength, swapNumMax, processingZoneSwapFraction, greedySpread, storeAllBestprocessingBlockArrangement, echo):
    '''
    This function performs the Tabu search! 

    What is the tabu search? 

    The idea is that a tabu list is stored. This tabu list contains previously visited solutions. 
    A local search in the neighbourhood of a current solution and jumps to the best solution, given it is not on the tabu list. Note that the best solution can also be locally worsening. 

    The tabu list is of finite size and upon adding a new element to it, the oldest element in the list gets deleted. 

    The algorithm remembers the best solution so far and returns it after a given number of iterations. 

    How do we go about this. We perform the whole tabu search algorithm in three steps: 
        
        1.  Optimize the arrangement of the processing blocks. Swap whole procesing blocks (as opposed to only swapping processing zones)

        2.  Optimize the arrangement of the idle qubits within each layer. 
            Randomly pick a processing layer d and an an idle qubit from the corresponding idle pool 
            Compute cost metric for swapping it with all other idle qubits. 

        3.  Optimize the arrangement of the qubits within the processing blocks. 
            Randomly pick a layer, a processing block and a qubit within this processing block, either active or idle. 
            Compute the cost metric of swapping this qubit with all other qubits in the *same* processing zone. 


    Accepts: 
        processingBlockArrangement:                             Output of improvePlacement in the optimizing.py file 
        Fsizes:                         Table of idle storage zone capacities
        qMax:                           Processing zone capacity
        mMax:                           Number of processing zones
        nQ:                             Number of qubits
        TSiterations:                   Number of TabuSearch steps (e.g. 5000) 
        tabuListLength:                          Size of the Tabu list 
        swapNumMax:                     Maximum nuber of Qubits to be swapped during one TabuSearch step
        processingZoneSwapFraction:     How many of the TS steps are ones where entire processing zones are swapped? Relatively speaking 
        greedySpread:                   I dont know 
        storeAllBestprocessingBlockArrangement:                 I dont understand 
        echo:                           Prints debug output 

    Returns: 
        processingBlockArrangementnew                           Reconstructed processingBlockArrangement list based on optimized Y position list 
        costProgressList                 List that keeps track of total cost for every iteration of the TS algorithm 
        bestcostProgressList             List that keeps track of the best cost so far. Does not decrease
        Ybest                           Best arrangement of Y positions found by the TS algorithm 
        numberOfImprovingSteps                 Number of TS steps where the cost was actually minimized 
        numberOfTabuSteps                         Number of events where a swap is not allowed / tabu
        numberOfStepsWithoutUpdate                     Number of TS steps where no update has been done 
        bestYAll                        List that keeps track of all intermediate arrangements of Y positions, where improved (cost decreased)
        bestCostUpdateAll               
        bestprocessingBlockArrangementTblAll                    List of all intermediate B lists where TS step led to improvement 
        (TStime                          absolute runtime... later)

    '''

    # initialize all variables

    # number of storage zones 
    numberOfStorageZones = len(Fsizes)

    # number of blocks (steps)
    numberOfProcessingBlocks = len(processingBlockArrangement)

    # idlepool to be filled 
    idlePools = []
    
    # processingpool to be filled 
    processingPools = []

    # Table of processing zone number for the qubits? 
    zoneNumberList = []

    # corresponds to a table of s values ('p' or 'i')
    zoneStatusList = []

    # corresponds to a talbe of s' values ('a' or 'i')
    natureStatusList = []

    # table of qubits I guess 
    listOfAllQubits = [q for q in range(nQ)]


    # iterate over all the blocks - put togehter all the list we are going to need to update. In the end, we're gonna assemble all of these into a B list 
    for processingBlock in range(numberOfProcessingBlocks):

        # define the S list for every step 
        # SP = processingBlockArrangement[processingBlock][0]

        # define c list for every step 
        pointerQuadruple = processingBlockArrangement[processingBlock][3]
        
        # list of idle qubits? 
        idleList = []

        # position in processing zone? 
        processingList = [[] for _ in range(len(processingBlockArrangement[processingBlock][1]))]

        # 
        zonesList = [0] * nQ

        tempZoneStatusList = [0] * nQ

        tempNatureStatusList = [0] * nQ

        # put together the list of qubits in processing and idle zones, fill the according lists iteratively 
        for qubitNo in range(nQ):
            if pointerQuadruple[qubitNo][3] == 'i': 
                idleList.append(qubitNo)
            else: 
                processingList[pointerQuadruple[qubitNo][1]].append(qubitNo)
            
            zonesList[qubitNo] = pointerQuadruple[qubitNo][1]

            tempZoneStatusList[qubitNo] = pointerQuadruple[qubitNo][0]

            tempNatureStatusList[qubitNo] = pointerQuadruple[qubitNo][3]

        # Idlepools is structured like [[idle list block one], [idle list block two], ...]
        idlePools.append(idleList)

        # same for processingpools 
        processingPools.append(processingList)

        # same for numbers of processing zones I guess 
        zoneNumberList.append(zonesList)

        # those are just lists of lists of strings ('i' and 'p', or 'i' and 'a') indicating the property for each qubit 
        zoneStatusList.append(tempZoneStatusList)
        natureStatusList.append(tempNatureStatusList)



    # create the list of Y positions
    Y = computeArrangements(processingBlockArrangement, Fsizes, qMax)

    # compute total cost 
    costTot = computeTotalCost(Y, nQ)


    if echo == True:

        print('Debug output')


    '''
    We have created or extracted all the lists we need to perform the Tabu Search. Now, the Tabu Search can begin. 

    TABU SEARCH 
    '''

    # tabu list, to be filled iteratively with Y lists. So with arrangements of Y positions corresponding to processing blocks that are not allowed 
    tabuList = [0] * tabuListLength

    # position of current element in tabu list, first element is at zepermutationPositionh position, so positionInTabuList = 0. 
    # After adding an element to the tabu list, we increase this counter 
    positionInTabuList = 0

    # number of TS steps where improvement was found 
    numberOfImprovingSteps = 0

    # number of TS steps where a step was tabu 
    numberOfTabuSteps = 0 

    # number of steps where no update was done
    numberOfStepsWithoutUpdate = 0

    # No idea 
    memberQqueries = 0

    # Just for debugging reasons... Keep track of the number of steps where more than two, or only two qubits were swapped 
    numberOfMultipleSwapSteps = 0
    numberOfOneSwapSteps = 0

    # How many of those were processing zone swaps? 
    numberOfProcessingZoneSwapSteps = 0

    # Number of steps where we improved upon swapping processing zones? 
    numImprovementsAfterProcessingZoneSwaps = 0

    # costBest so far is just the total cost 
    costBest = costTot

    # Best arrangement of qubits is so far the one we have now 
    YBest = Y

    # keep track of cost over the iterations
    costProgressList = [[] for _ in range(TSiterations)]

    # keep track of best cost over iterations 
    bestcostProgressList = [[] for _ in range(TSiterations)]

    # keep track of arrangements of processing zones for qubits corresponding to the arrangements that minimize the cost, I guess... 
    zoneNumberListBest = zoneNumberList

    # and then this, as always 
    zoneStatusListBest = zoneStatusList
    natureStatusListBest = natureStatusList

    # I ADDED THIS, IDK MAYBE WRONG, but why should it be wrong? 
    # if we focus on exchanging processing zones, the number just decreases to one
    numPossibleSwaps = swapNumMax 
    # also set this to false, can be set to true in the according section... just so we dont get a referenced before assignment error 
    swapProcessingZones = False

    newProcessingBlockArrangement = processingBlockArrangement

    # for animation reasons 
    processingBlockArrangementDisplaying = []

    # at this point, the stuff is also timed 
    # and reap and sow again due to displaying and developement reasons 

    # this is the Tabu Search; iterate TSiterations times. 
    for iterationStep in range(TSiterations): 
        

        '''
        Identifying the qubits to be swapped 
        '''


        # choose processing block at random 
        processingBlock = random.randint(0, numberOfProcessingBlocks-1) 

        # if we can not swap whole processing zones anymore? 
        if iterationStep >= processingZoneSwapFraction:

            # Choose a qubit at random
            qubit1 = random.randint(0, nQ-1) 

            # zoneStatusQubitOne is either 'i' or 'p', in what kinda zone is qubit1? 
            zoneStatusQubitOne = zoneStatusList[processingBlock][qubit1]

            # natureStatusQubitOne is either 'a' or 'i', what kinda qubit is it? 
            natureStatusQubitOne = natureStatusList[processingBlock][qubit1]

            # what processing zone number does qubit1 sit in 
            processingZoneNumberQubitOne = zoneNumberList[processingBlock][qubit1]
             
            # Chooose how many qubits should be exchanged in this step 
            numberOfQubitsToBeSwapped = random.randint(2, swapNumMax)


            # We picked a qubit, but we have no idea where it sits in or if it is active or idle. So we have to, based on these facts, 
            # identify some properties of this qubit 

            '''
            Create swappools, so list of possible swap partners for qubit1 
            '''

            # if qubit1 is of idle nature
            if natureStatusQubitOne == "i":

                # if qubit1 is idle, all the qubits that are idle in this very processing zone are potential swapping partners. 
                swapPool = idlePools[processingBlock]

                # if qubit1 is in a processing zone and if we want to exchange two qubits in this step 
                if zoneStatusQubitOne == 'p' and numberOfQubitsToBeSwapped == 2: 

                    # the swappool now consists of all the idle qubits in this processing block as well as the ones that are in the same processing zone as qubit1 
                    swapPool = swapPool + processingPools[processingBlock][processingZoneNumberQubitOne]

            else: 

                # whyever this should occur?? 
                if processingZoneNumberQubitOne > mMax:
                    print('Eror, apparently something is horribly wrong. ')
                    break 

                # if qubit1 is active, it sits in a processing zone. Then the possible swap partners for qubit1 are only the qubits that sit in the very same processing zone. 
                swapPool = processingPools[processingBlock][processingZoneNumberQubitOne]

            # qubit1 cannot be swapped with itself, remove it from the list of possible swap partners, if its in there, I guess
            if qubit1 in swapPool: 
                swapPool.remove(qubit1)
            # else: 
                # print('qubit1 not in swapPool????')

            # how many qubits in total are possible swap partners for qubit1? 
            swapPoolSize = len(swapPool)



            # if we want to exchange more qubits than are possible, given by the size of the swappool 
            # if we want to exchange two, the swappool has to have at least 2-1 = 1 qubits. If less than one - we have to act. 
            if swapPoolSize < numberOfQubitsToBeSwapped - 1:
               
                # decrease the number of qubits we want to exchange to the number of qubits that are potential swap partners 
                numberOfQubitsToBeSwapped = swapPoolSize

            # the itertools.combinations() function gives us all possible combinations of 2 elements from the list
            # e.g. we want to swap 3 qubits and we have a swappool = [1,2,3]
            # temporarySubset would be [(1,2), (1,3), (2,3)]
            if numberOfQubitsToBeSwapped > 0:
                temporarySubset = list(itertools.combinations(swapPool, numberOfQubitsToBeSwapped - 1))
            else: 
                temporarySubset = list(itertools.combinations(swapPool, numberOfQubitsToBeSwapped))

            # IMPORTANT: 
            # temporarySubset consits of lists of qubits that act as possible swap partners! These individual lists can contain 1, 2 ... - up to 
            # swapnQBnum - 1 elements. 
            # One of the elements in the temporarySubset list will be chosen to swap qubit one with later one, based on which of these possible 
            # swaps minimizes the cost!!!  

            # the len of the list, as indicated above, indicates how many times we swap in total (taking into account also the total number of qubits that are available for swapping - through swapPool)
            numPossibleSwaps = len(temporarySubset)

            # permutationPosition seems to be a random integer, that controls the swapping and creation of the swappedQubitsToBeSwapped list 
            # why is it -2? That's because we want to assign an equal probability for all permutations, and permutationPosition = 0 achieves the same permutation as permutationPosition = numberOfQubitsToBeSwapped 

            '''
            I just altered this from -2 to -1 !!!
            This has to go later, in the end the swapPool cannot have size 0! This just cannot be -> debug 
            '''
            if numberOfQubitsToBeSwapped > 1: 
                # permutationPosition == 0 is not allowed, we *have* to swap the qubits. i guess...
                permutationPosition = random.randint(1, numberOfQubitsToBeSwapped-1)
            else: 
                permutationPosition = 0 # random.randint(0, 0)

            # here, we create the actual list of qubits that shall be swapped. 
            # using the example above, lets assume we already picked qubit 4 to be swapped: 
            # qubitsToBeSwapped = [[4] + list((1,2)), [4] + list((1,3)) + [4] + list((2,3))] = [[4,1,2], [4,1,3], [4,2,3]]
            qubitsToBeSwapped = [[qubit1] + list(subset) for subset in temporarySubset]

            # for every element in this swapQBList we iterate over all the sublists and do: 
            # swappedQubitsToBeSwapped = [4,1,2][permutationPosition:] + [4,1,2][:permutationPosition]
            # Let's assume permutationPosition = 1
            # swappedQubitsToBeSwapped = [1,2] + [4] = [1,2,4]
            # What is effectively done is, the qubits in the list are permuted by a random factor 
            # (here, it is clear why we chose -2 above; permutationPosition = 0 and permutationPosition = 2 would achieve exactly the same swappedQubitsToBeSwapped)
            swappedQubitsToBeSwapped = [qubitsToBeSwapped[ssi][permutationPosition:] + qubitsToBeSwapped[ssi][:permutationPosition] for ssi in range(len(qubitsToBeSwapped))]


        # In case we want to exchange whole processing zones / and still can 
        else: 

            # I guess, if there is only one processing zone, we can skip this step 
            if mMax > 1: 

                # swap two entire processing zones 
                swapProcessingZones = True 

                # increase this, obviously 
                numberOfProcessingZoneSwapSteps += 1 

                # we want to swap two processing zones, choose 2 numbers from all the processing zones, processingZonesToBeSwapped is a list  
                processingZonesToBeSwapped = random.sample(range(mMax), 2)

                # get all the qubits in the two processing zone numbers of the processing zones to be exchanged 
                # remember: listOfAllQubits = [q for q in range(nQ)] = [1,2,3,4,5,6,...,nQ]
                # qubits corresponding to number of first processing zone 
                qubitsInProcessingZone1 = [qubit for qubit in listOfAllQubits if zoneStatusList[processingBlock][qubit] == "p" and zoneNumberList[processingBlock][qubit] == processingZonesToBeSwapped[0]]

                # qubits corresponding to number of second processing zone 
                qubitsInProcessingZone2 = [qubit for qubit in listOfAllQubits if zoneStatusList[processingBlock][qubit] == "p" and zoneNumberList[processingBlock][qubit] == processingZonesToBeSwapped[1]]

                # The list now contains two elements, the two qubit lists 
                qubitsToBeSwapped = [qubitsInProcessingZone1 + qubitsInProcessingZone2]

                # Also, the list in other direction 
                swappedQubitsToBeSwapped = [qubitsInProcessingZone2 + qubitsInProcessingZone1]

                # qubitsToBeSwapped = [[qubit1, q2, ...]], so: 
                # numberOfQubitsToBeSwapped is the number of qubits that have to change their position due to swapping with some partner 
                numberOfQubitsToBeSwapped = len(qubitsToBeSwapped[0])

                # we only want to allow a limited number of processing zone swaps, namely one
                numPossibleSwaps = 1 


            # Hmm, i dont know, i added this...
            else: 
                continue
        
        '''
        Swapping the qubits and evaluating cost 
        '''

        # initialize single iteration step 
        # delta cost will indicate how much we can bring the cost down. The difference between the initial cost and the cost after swapping. We want to make this as small as possible.
        differenceToCostBeforeSwapping = 1000000 

        '''
        Get Y lists 
        '''

        # get the Y list corresponding to this particular block 
        Yc = Y[processingBlock]

        # if there's a block to the left, define the corresponding Y list 
        if processingBlock > 1: 
            Yp = Y[processingBlock-1]

        # if not, dont define it. 
        else: 
            Yp = [0] * nQ

        # if there's a block to the right, define the corresponding Y list 
        if processingBlock < numberOfProcessingBlocks-1: 
            Yf = Y[processingBlock + 1]

        # if not, dont 
        else: 
            Yf = [0] * nQ

        # What we do here is the following: 
        # we take the Y positions corresponding to the qubits that we want to exchange (in case of complete processing zones, exchange all of the qubits in the processing zones)
        # We calculate 2* (to be swapped qubits in left processing block + to be swapped qubits in right processing block) * (qubits in this processing block - qubits in this processing block, but swapped )

        # I guess this is a list of len (numpossibleswaps) and for every swap it keeps track of the decreasement of the cost that has been done 

        '''
        TRY THIS FOR NOW!!!
        '''


        # I added this np.array() stuff, not believing that would work but apparently, it did 
        listOfCostsForDifferentSwaps = [2 * np.dot(np.array(Yp)[qubitsToBeSwapped[ssi]] + np.array(Yf)[qubitsToBeSwapped[ssi]], np.array(Yc)[qubitsToBeSwapped[ssi]] - np.array(Yc)[swappedQubitsToBeSwapped[ssi]]) for ssi in range(numPossibleSwaps)]

        # listOfCostsForDifferentSwaps = []

        # for i in range(numPossibleSwaps):
        #     Y_np = np.array(Y)
        #     Y_original = np.array(Y)
        #     Y_np[step][qubitsToBeSwapped] = Y_original[step][swappedQubitsToBeSwapped]
        #     cost_temp = computeTotalCost(Y_np, nQ)
        #     listOfCostsForDifferentSwaps.append(cost_temp)



        # orders the costs by swaps 
        orderedCostIndices = np.argsort(listOfCostsForDifferentSwaps)


        '''
        WHAT EXACTLY DOES ORD LOOK LIKE?? 
        '''


        # ordering the deltacost table to see which swap minimizes the cost 
        listOfCostsForDifferentSwaps = np.array(listOfCostsForDifferentSwaps)[orderedCostIndices]

        # orders the qubits in the swaplist corresponding to the order 
        qubitsToBeSwapped = [qubitsToBeSwapped[ssi] for ssi in orderedCostIndices]

        # Also the swapped qubits i suppose 
        swappedQubitsToBeSwapped = [swappedQubitsToBeSwapped[ssi] for ssi in orderedCostIndices]


        '''
        Performing the update, updating the Tabu list and all the lists corresponding to the best values 
        '''


        # if flag == false; no update will be performed, the tabu list will not be updated!! 
        # 'RESET' FLAG TO FALSE
        flag = False 

        # iterate over the number of possible swaps 
        for swapNo in range(numPossibleSwaps):
               
            
            YTest = np.array(Y) 

            # for every swap, exchange the positions in the Y list corresponding to the qubits in the swapQBlist with the qubits in qubitsToBeSwappedwapped 
            # remember: swapQBList contains all qubits that will swap their partner
            # swappedQubitsToBeSwapped contains all the qubits that shall be swapped, but in the order they are to be swapped to 
            YTest[processingBlock][qubitsToBeSwapped[swapNo]] = YTest[processingBlock][swappedQubitsToBeSwapped[swapNo]]

            # 
            memberQqueries += 1


            if np.any(np.all(YTest == tabuList)):
            # if YTest in tabuList:
                numberOfTabuSteps += 1 

                # jump to next swap 
                continue 

            # if not in tabu list update best local cost, set update flag true and save swapped arrangement 
            # an update shall be performed later 
            flag = True 

            # differenceToCostBeforeSwapping can be worse than the best cost so far. 
            # We did not check for the quality of the cost yet. 
            differenceToCostBeforeSwapping = listOfCostsForDifferentSwaps[swapNo]

            # save corresponding Y  
            YBestUpdate = YTest

            # save corresponding processing zone constellation 
            zoneNumberListBestUpdate = np.array(zoneNumberList)

            # save s1, s2 tables 
            zoneStatusListBestUpdate = np.array(zoneStatusList)
            natureStatusListBestUpdate = np.array(natureStatusList)

            # and swap zones and s1. 
            # s2 unaffected 
            zoneNumberListBestUpdate[processingBlock][qubitsToBeSwapped[swapNo]] = zoneNumberListBestUpdate[processingBlock][swappedQubitsToBeSwapped[swapNo]]
            zoneStatusListBestUpdate[processingBlock][qubitsToBeSwapped[swapNo]] = zoneStatusListBestUpdate[processingBlock][swappedQubitsToBeSwapped[swapNo]]



            # I guess greedyspread means more than one swap at a time 
            if greedySpread == False:
                break



























            '''
            Greedy Search:

            Try to update arrangement on blocks left and right of the current block 
            '''

            # define this for the while-loop 
            # start with block on the right of current block 
            greedyProcessingBlock = processingBlock + 1 

            # while we did not reach the number of processing blocks 
            # iterate over all the layers that are on the right of the current block 
            while greedyProcessingBlock < numberOfProcessingBlocks - 1: 
                
                # I do not understand this. 
                # if the qubits that shall be swapped in the step layer do not have the same nature ('a' or 'i') in the next layer, break 
                # also, if these two sets of qubits are in different processing zones, break 
                if natureStatusList[processingBlock][qubitsToBeSwapped[swapNo]] != natureStatusList[greedyProcessingBlock][qubitsToBeSwapped[swapNo]] or  zoneNumberList[processingBlock][qubitsToBeSwapped[swapNo]] != zoneNumberList[greedyProcessingBlock][qubitsToBeSwapped[swapNo]]:
                    break

                # update the Y lists as well 
                currentYPositionList = YBestUpdate[greedyProcessingBlock]
                previousYPositionList = YBestUpdate[greedyProcessingBlock - 1]
              
                # if there's a right neighbour, do the same 
                if greedyProcessingBlock < numberOfProcessingBlocks: 
                    nextYPositionList = YBestUpdate[greedyProcessingBlock + 1]
                else: 
                    nextYPositionList = [0] * nQ
              
                # same as above 
                deltaCost2 = 2 * (previousYPositionList[qubitsToBeSwapped[swapNo]] + nextYPositionList[qubitsToBeSwapped[swapNo]]) * (currentYPositionList[qubitsToBeSwapped[swapNo]] - currentYPositionList[swappedQubitsToBeSwapped[swapNo]])
              
                # update the best lists for greedyProcessingBlock!! as well. We did it for step above, but now also for greedyProcessingBlock
                if deltaCost2 < 0: 
                    differenceToCostBeforeSwapping += deltaCost2
                
                    YBestUpdate[greedyProcessingBlock][qubitsToBeSwapped[swapNo]] = YBestUpdate[greedyProcessingBlock][swappedQubitsToBeSwapped[swapNo]]
                
                    zoneNumberListBestUpdate[greedyProcessingBlock][qubitsToBeSwapped[swapNo]] = zoneNumberListBestUpdate[greedyProcessingBlock][swappedQubitsToBeSwapped[swapNo]]
                    zoneStatusListBestUpdate[greedyProcessingBlock][qubitsToBeSwapped[swapNo]] = zoneStatusListBestUpdate[greedyProcessingBlock][swappedQubitsToBeSwapped[swapNo]]
                
                    for sqbi in range(qubitsToBeSwapped[swapNo]): 
                        sqb = qubitsToBeSwapped[swapNo][sqbi]
                 
                    if zoneStatusListBestUpdate[greedyProcessingBlock][sqb] == "i" and natureStatusListBestUpdate[greedyProcessingBlock][sqb] == "a":
                        print("  ERROR in greedy expansion, step: ", processingBlock)
                else: 
                    greedyProcessingBlock = numberOfProcessingBlocks
                
                greedyProcessingBlock += 1 


            # block on the left of current block 
            greedyProcessingBlock = processingBlock - 1 

            # iterate over all the layers that are on the left of the current block 
            while greedyProcessingBlock > 0: 


                # Muss noch geandert werden!! 


                if natureStatusList[processingBlock][qubitsToBeSwapped[swapNo]] != natureStatusList[processingBlock][qubitsToBeSwapped[swapNo]] or  zoneNumberList[processingBlock][qubitsToBeSwapped[swapNo]] != zoneNumberList[greedyProcessingBlock][qubitsToBeSwapped[swapNo]]:
                    break

                currentYPositionList = YBestUpdate[greedyProcessingBlock]
                previousYPositionList = YBestUpdate[greedyProcessingBlock - 1]
              
                if greedyProcessingBlock < numberOfProcessingBlocks: 
                    nextYPositionList = YBestUpdate[greedyProcessingBlock + 1]
                else: 
                    nextYPositionList = [0] * nQ
              
                deltaCost2 = 2 * (previousYPositionList[qubitsToBeSwapped[swapNo]] + nextYPositionList[qubitsToBeSwapped[swapNo]]) * (currentYPositionList[qubitsToBeSwapped[swapNo]] - currentYPositionList[swappedQubitsToBeSwapped[swapNo]])
              

                if deltaCost2 < 0: 
                    differenceToCostBeforeSwapping += deltaCost2
                
                    YBestUpdate[greedyProcessingBlock][qubitsToBeSwapped[swapNo]] = YBestUpdate[greedyProcessingBlock][swappedQubitsToBeSwapped[swapNo]]
                
                    zoneNumberListBestUpdate[greedyProcessingBlock][qubitsToBeSwapped[swapNo]] = zoneNumberListBestUpdate[greedyProcessingBlock][swappedQubitsToBeSwapped[swapNo]]
                    zoneStatusListBestUpdate[greedyProcessingBlock][qubitsToBeSwapped[swapNo]] = zoneStatusListBestUpdate[greedyProcessingBlock][swappedQubitsToBeSwapped[swapNo]]
                
                    for sqbi in range(qubitsToBeSwapped[swapNo]): 
                        sqb = qubitsToBeSwapped[swapNo][sqbi]
                 
                    if zoneStatusListBestUpdate[greedyProcessingBlock][sqb] == "i" and natureStatusListBestUpdate[greedyProcessingBlock][sqb] == "a":
                        print("  ERROR in greedy expansion, step: ", processingBlock)
                else: 
                    greedyProcessingBlock = 1
                
                greedyProcessingBlock -= 1 

            # this loop is breaked here:  for ssi in range(numPossibleSwaps)
            # we do not iterate over the possible swaps anymore. In the algorithm, now we deal with what comes after the swapping, all the swapping is finished. Now, for the updating 
            break  

        '''
        GreedySpread over! 
        '''
















        '''
        Swapping is finished -> Updating 
        '''

        # no update if flag == false
        # if flag == false, this means that no idea  
        if flag == False: 
            numberOfStepsWithoutUpdate += 1 

        # if flag == true, update tabu list and all the best lists, and ggf bestcost 
        if flag == True: 

            # assign this Y to the corresponding element in the tabu list, why not just use append? 
            tabuList[positionInTabuList] = YBestUpdate

            # increase counter by one 
            positionInTabuList += 1

            # when we have reached the end of the tabu list: start filling the tabu list, starting at the oldest - the first - element again 
            if positionInTabuList >= tabuListLength: 
                positionInTabuList = 0

            # HERE
            # IS WHERE THE ACTUAL SWAPPING OF THE Y LIST IS HAPPENING
            Y = YBestUpdate 

            # update zones
            zoneNumberList = zoneNumberListBestUpdate

            # update s1, s2 
            zoneStatusList = zoneStatusListBestUpdate
            natureStatusList = natureStatusListBestUpdate

            # update total cost 
            costTot += differenceToCostBeforeSwapping

            # if, globally, cost is minimal: 
            if costTot < costBest: 

                # global best cost is current cost 
                costBest = costTot 

                # and all the other best lists get updated too 
                YBest = YBestUpdate
                zoneNumberListBest = zoneNumberListBestUpdate
                zoneStatusListBest = zoneStatusListBestUpdate
                natureStatusListBest = natureStatusListBestUpdate

                # increase counter, because right now we have improved the cost!
                numberOfImprovingSteps += 1 

                # if we want to store all of the improvements on b that are made in the course of this algorithm 
                if storeAllBestprocessingBlockArrangement == True: 

                    # save it by reconstructing the blocks, given the old processingBlockArrangement as well as the Y, optimized by the tabu search 
                    newProcessingBlockArrangement = reconstructBlocksFromArrangements(processingBlockArrangement, Fsizes, qMax, mMax, nQ, YBest, zoneNumberListBest, zoneStatusListBest, natureStatusListBest)

                # Taking care of some counters 
                if swapProcessingZones == False: 
                    if numberOfQubitsToBeSwapped > 2: 
                        numberOfMultipleSwapSteps += 1 

                    else: 
                        numberOfOneSwapSteps += 1

                if swapProcessingZones == True:
                    numImprovementsAfterProcessingZoneSwaps += 1

                processingBlockArrangementDisplaying.append(copy.deepcopy(newProcessingBlockArrangement))


            # if we did not improve upon the best cost yet, set local delta cost to zero 
            else: 
                differenceToCostBeforeSwapping = 0 


        # take care of the two cost tables
        costProgressList[iterationStep] = [iterationStep, costTot]
        bestcostProgressList[iterationStep] = [iterationStep, costBest]



    # here is still a lot missing for I guess graphic and debugging purposes, first I have to try to understand this algorithm 

    '''
    All done 
    '''

    return newProcessingBlockArrangement, costProgressList, bestcostProgressList, YBest, numberOfImprovingSteps, numberOfTabuSteps, numberOfStepsWithoutUpdate, processingBlockArrangementDisplaying
            

newProcessingBlockArrangement, costProgressList, bestcostProgressList, YBest, numberOfImprovingSteps, numberOfTabuSteps, numberOfStepsWithoutUpdate, processingBlockArrangementDisplaying = improvePlacementTabuSearch(processingBlockArrangementAfterOptimizing, FSIZES, QMAX, MMAX, NQ, TSiterations=600, tabuListLength=30, swapNumMax=3, processingZoneSwapFraction=0, greedySpread=False, storeAllBestprocessingBlockArrangement=True, echo=True)

'''
Plotting cost evolution
'''

# print(costProgressList)

cost_list = []
for i in range(1, len(costProgressList)):
    cost_list.append(costProgressList[i][1])

best_cost_list = []
for i in range(1, len(bestcostProgressList)):
    best_cost_list.append(bestcostProgressList[i][1])

title = str(numberOfImprovingSteps) + '#tabus: ' + str(numberOfTabuSteps) + '#noUpdates: ' + str(numberOfStepsWithoutUpdate)

# plt.figure()
# plt.plot(cost_list, label = 'cost')
# plt.plot(best_cost_list, label = 'best cost')
# plt.title('Evolution of the cost with the iterations, #impr: ' + title + '\n')
# plt.xlabel('Iterations')
# plt.ylabel('Cost')
# plt.legend()
# plt.show()

# print('B is: \n', B)
# print('newProcessingBlockArrangement is: \n', newProcessingBlockArrangement)

# visualize_blocks(newProcessingBlockArrangement, 'After Tabu Search, cost: ' + str(computeTotalCost(YBest, NQ)) + ', # tabusteps: ' + str(numberOfTabuSteps))


# animate_solving(processingBlockArrangementDisplaying, 'tabu search animation, cost: ' + str(computeTotalCost(YBest, NQ)) + ', # tabusteps: ' + str(numberOfTabuSteps))


