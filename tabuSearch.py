import numpy as np
import matplotlib.pyplot as plt
# import random 
import itertools 
from optimizing import *



print('###########')
print('Tabu Search')
print('###########')

def reconstructBlocksFromArrangements(BPold, Fsizes, Qmax, Mmax, Nq, Y, zonesTbl, s1Tbl, s2Tbl):
    '''
    This function iteratively creates a new B list, given an old B list and a corresponding list with Y positions. 

    It rearranges the qubits in the B list according to the list of y positions Y. 

    For each element in the Y list, it creates a processing block in the new B list. 


    For efficiency reasons, the tabu search algorithm below does not operate on the BP data structure itself.  
    It merely updates the list of Y positions, the zone tables and the s1 Tables. (s2 never changes, an active qubit stays active, an idle qubit stays idle)
    For this reason, this function, after the execution of the Tabu Search, rebuilds the BP list, most importantly the c list
    
    Accepts: 

        BPold:          input BP structure
        Fsizes:         table of idle storage zone capacities
        Qmax:           Processing zone capacity
        Mmax:           Number of processing zones
        Nq:             Number of qubits
        Y:              arrangements, output of tabu search
        zonesTbl:       table of zone indices for each step, output of tabu search
        s1Tbl:          table of QB status "i" or "p", output of tabu search
        s2Tabl:         table of QB status "a" or "i", not affected by tabu search

    Returns:

        BPnew:          reconstructed BP structure

    '''

    # create new B list to be filled iteratively
    BPnew = []

    # create a table of qubits? 
    qbTbl = np.arange(Nq)
    
    # iterate over all the blocks in the Y list 
    for step in range(len(Y)):

        # get the list of the qubits in this step, [::-1] reverses the list 
        qbTblSort = qbTbl[np.argsort(Y[step])][::-1]

        # get the old GP, this will stay the same. Remember: The gates that are covered will not change, since the qubits will not move in- or out of the processing zones. Only their arrangements within the processing 
        # zones will be adapted. 
        GP = BPold[step][1]

        # create a new S array to be filled
        # SPnew = ([[[[], []] for _ in range(Mmax)] for _ in range(Mmax)])

        SPnew = [[] for _ in range((Mmax))]

        # create a new F array to be filled 
        FPnew = [[] for _ in range(len(Fsizes))]

        # create a new c array to be filled 
        cNew = [[] for _ in range(Nq)]

        # for processing and idle qubits, create empty arrays to be filled with positions?
        # processing zone qubits 
        kpTbl = np.ones(Mmax, dtype=int)

        # idle zone qubits 
        kiTbl = np.ones(len(Fsizes), dtype=int)
        
        # iterate over all qubits in the processing block 
        for qi in range(Nq):

            # get qubit corresponding to number qi 
            q = qbTblSort[qi]

            # WHAT EXACTLY DO S1TBL AND S2TBL DO? 
            # s1 corresponds to s, s2 corresponds to s', meaning: 
            # s1 indicates if the qubit is stored in idle or processing zone 
            s1 = s1Tbl[step][q]

            # s2 indicates if the qubit is active or idle 
            s2 = s2Tbl[step][q]

            # processing zone number?
            z = zonesTbl[step][q]
            
            # if the qubit is stored in idle zone 
            if s1 == "i":

                # use the kiTbl for the position within the zone, corresponding to idle qubits 
                cNew[q] = [s1, z, kiTbl[z], s2]

                # the next qubit has a position in the zone z that is one larger 
                kiTbl[z] += 1

                # and adjust the idle zone list accordingly 
                FPnew[z].append(q)

            # if the qubit is stored in processing zone 
            else:

                # use position list corresponding to processing zones 
                cNew[q] = [s1, z, kpTbl[z], s2]

                # increase position by one 
                kpTbl[z] += 1

                # append qubit in processing zone to Slist 
                SPnew[z].append(q)


                # KOKOLORES
                # if it is an active qubit in a processing zone 
                # if s2 == "a":

                #     # store it in the first position in the SPnew list S = [[active, idle], [active, idle] ... , [active, idle]]
                #     SPnew[z][0][0].append(q)

                # # if it is an idle qubit in a processing zone 
                # else:

                #     # store it in the according position 
                #     SPnew[z][0][1].append(q)
        
        # we create the new B iteratively, for each step in the Y list 
        BPnew.append([SPnew, GP, FPnew, cNew])
    
    # return the new B list 
    return BPnew



'''
We can now update a B list given an old B list and a 'new' Y list that has been created by the tabu search. 
Now for the actual tabu search. 
'''


def improvePlacementTabuSearch(BP, Fsizes, Qmax, Mmax, Nq, TSiterations, TSlen, swapNumMax, processingZoneSwapFraction, greedySpread, storeAllBestBP, echo):
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
        BP:                             Output of improvePlacement in the optimizing.py file 
        Fsizes:                         Table of idle storage zone capacities
        Qmax:                           Processing zone capacity
        Mmax:                           Number of processing zones
        Nq:                             Number of qubits
        TSiterations:                   Number of TabuSearch steps (e.g. 5000) 
        TSlen:                          Size of the Tabu list 
        swapNumMax:                     Maximum nuber of Qubits to be swapped during one TabuSearch step
        processingZoneSwapFraction:     How many of the TS steps are ones where entire processing zones are swapped? Relatively speaking 
        greedySpread:                   I dont know 
        storeAllBestBP:                 I dont understand 
        echo:                           Prints debug output 

    Returns: 
        BPnew                           Reconstructed BP list based on optimized Y position list 
        costProgressTbl                 List that keeps track of total cost for every iteration of the TS algorithm 
        bestCostProgressTbl             List that keeps track of the best cost so far. Does not decrease
        Ybest                           Best arrangement of Y positions found by the TS algorithm 
        numImprovements                 Number of TS steps where the cost was actually minimized 
        tabuCtr                         Number of events where a swap is not allowed / tabu
        noUpdateCtr                     Number of TS steps where no update has been done 
        bestYAll                        List that keeps track of all intermediate arrangements of Y positions, where improved (cost decreased)
        bestCostUpdateAll               
        bestBPTblAll                    List of all intermediate B lists where TS step led to improvement 
        (TStime                          absolute runtime... later)

    '''

    # initialize all variables

    # number of storage zones 
    numF = len(Fsizes)

    # number of blocks (steps)
    numSteps = len(BP)

    # idlepool to be filled 
    idlePools = []
    
    # processingpool to be filled 
    processingPools = []

    # Table of processing zone number for the qubits? 
    zonesTbl = []

    # corresponds to a table of s values ('p' or 'i')
    s1Tbl = []

    # corresponds to a talbe of s' values ('a' or 'i')
    s2Tbl = []

    # table of qubits I guess 
    QBTbl = [q for q in range(Nq)]


    # iterate over all the blocks - put togehter all the list we are going to need to update. In the end, we're gonna assemble all of these into a B list 
    for step in range(numSteps):

        # define the S list for every step 
        SP = BP[step][0]

        # define c list for every step 
        c = BP[step][3]
        
        # list of idle qubits? 
        idleList = []

        # position in processing zone? 
        processingList = [[] for _ in range(len(BP[step][1]))]

        # 
        zonesList = [0] * Nq

        s1List = [0] * Nq

        s2List = [0] * Nq

        # put together the list of qubits in processing and idle zones, fill the according lists iteratively 
        for q in range(Nq):
            if c[q][3] == 'i': 
                idleList.append(q)
            else: 
                processingList[c[q][1]].append(q)
            
            zonesList[q] = c[q][1]

            s1List[q] = c[q][0]

            s2List[q] = c[q][3]

        # Idlepools is structured like [[idle list block one], [idle list block two], ...]
        idlePools.append(idleList)

        # same for processingpools 
        processingPools.append(processingList)

        # same for numbers of processing zones I guess 
        zonesTbl.append(zonesList)

        # those are just lists of lists of strings ('i' and 'p', or 'i' and 'a') indicating the property for each qubit 
        s1Tbl.append(s1List)
        s2Tbl.append(s2List)



    # create the list of Y positions
    Y = computeArrangements(BP, Fsizes, Qmax)

    # compute total cost 
    costTot = computeTotalCost(Y, Nq)


    if echo == True:

        print('Debug output')


    '''
    We have created or extracted all the lists we need to perform the Tabu Search. Now, the Tabu Search can begin. 

    TABU SEARCH 
    '''

    # tabu list, to be filled iteratively with Y lists. So with arrangements of Y positions corresponding to processing blocks that are not allowed 
    TSList = [0] * TSlen

    # position of current element in tabu list, first element is at zeroth position, so tsfill = 0. 
    # After adding an element to the tabu list, we increase this counter 
    TSFill = 0

    # number of TS steps where improvement was found 
    numImprovements = 0

    # number of TS steps where a step was tabu 
    tabuCtr = 0 

    # number of steps where no update was done
    noUpdateCtr = 0

    # No idea 
    memberQqueries = 0

    # Just for debugging reasons... Keep track of the number of steps where more than two, or only two qubits were swapped 
    numImprovementMultiSwaps = 0
    numImprovementTwoSwaps = 0

    # How many of those were processing zone swaps? 
    numProcessingZoneSwaps = 0

    # Number of steps where we improved upon swapping processing zones? 
    numImprovementProcessingZonesSwaps = 0

    # costBest so far is just the total cost 
    costBest = costTot

    # Best arrangement of qubits is so far the one we have now 
    YBest = Y

    # keep track of cost over the iterations
    costProgressTbl = [[] for _ in range(TSiterations)]

    # keep track of best cost over iterations 
    bestCostProgressTbl = [[] for _ in range(TSiterations)]

    # keep track of arrangements of processing zones for qubits corresponding to the arrangements that minimize the cost, I guess... 
    zonesTblBest = zonesTbl

    # and then this, as always 
    s1TblBest = s1Tbl
    s2TblBest = s2Tbl

    # I ADDED THIS, IDK MAYBE WRONG, but why should it be wrong? 
    # if we focus on exchanging processing zones, the number just decreases to one
    numPossibleSwaps = swapNumMax 
    # also set this to false, can be set to true in the according section... just so we dont get a referenced before assignment error 
    swapProcessingZones = False

    bNew = BP

    # for animation reasons 
    bList = []

    # at this point, the stuff is also timed 
    # and reap and sow again due to displaying and developement reasons 

    # this is the Tabu Search; iterate TSiterations times. 
    for i in range(TSiterations): 
        

        '''
        Identifying the qubits to be swapped 
        '''


        # generate random number in range numSteps 
        # chooose random block 
        step = random.randint(0, numSteps-1) 

        # if we can not swap whole processing zones anymore? 
        if i >= processingZoneSwapFraction:

            # generate random integer between 0 and Nq-1 (both included)
            # look at random qubit in this block - what qubit do we want to switch? 
            # Choose a qubit at random
            q1 = random.randint(0, Nq-1) 

            # s1Swap is either 'i' or 'p', in what kinda zone is q1? 
            s1Swap = s1Tbl[step][q1]

            # s2Swap is either 'a' or 'i', what kinda qubit is it? 
            s2Swap = s2Tbl[step][q1]

            # what processing zone number does q1 sit in 
            processingZoneIndex = zonesTbl[step][q1]
             
            # Chooose how many qubits should be exchanged in this step 
            swapQBnum = random.randint(2, swapNumMax)


            # We picked a qubit, but we have no idea where it sits in or if it is active or idle. So we have to, based on these facts, 
            # identify some properties of this qubit 

            '''
            Create swappools, so list of possible swap partners for q1 
            '''

            # if q1 is of idle nature
            if s2Swap == "i":

                # if q1 is idle, all the qubits that are idle in this very processing zone are potential swapping partners. 
                swapPool = idlePools[step]

                # if q1 is in a processing zone and if we want to exchange two qubits in this step 
                if s1Swap == 'p' and swapQBnum == 2: 

                    # the swappool now consists of all the idle qubits in this processing block as well as the ones that are in the same processing zone as q1 
                    swapPool = swapPool + processingPools[step][processingZoneIndex]

            else: 

                # whyever this should occur?? 
                if processingZoneIndex > Mmax:
                    print('Eror, apparently something is horribly wrong. ')
                    break 

                # if q1 is active, it sits in a processing zone. Then the possible swap partners for q1 are only the qubits that sit in the very same processing zone. 
                swapPool = processingPools[step][processingZoneIndex]

            # q1 cannot be swapped with itself, remove it from the list of possible swap partners, if its in there, I guess
            if q1 in swapPool: 
                swapPool.remove(q1)
            # else: 
                # print('q1 not in swapPool????')

            # how many qubits in total are possible swap partners for q1? 
            swapPoolSize = len(swapPool)



            # if we want to exchange more qubits than are possible, given by the size of the swappool 
            # if we want to exchange two, the swappool has to have at least 2-1 = 1 qubits. If less than one - we have to act. 
            if swapPoolSize < swapQBnum - 1:
               
                # decrease the number of qubits we want to exchange to the number of qubits that are potential swap partners 
                swapQBnum = swapPoolSize

            # the itertools.combinations() function gives us all possible combinations of 2 elements from the list
            # e.g. we want to swap 3 qubits and we have a swappool = [1,2,3]
            # subsets would be [(1,2), (1,3), (2,3)]
            if swapQBnum > 0:
                subsets = list(itertools.combinations(swapPool, swapQBnum - 1))
            else: 
                subsets = list(itertools.combinations(swapPool, swapQBnum))

            # IMPORTANT: 
            # subsets consits of lists of qubits that act as possible swap partners! These individual lists can contain 1, 2 ... - up to 
            # swapNQBnum - 1 elements. 
            # One of the elements in the subsets list will be chosen to swap qubit one with later one, based on which of these possible 
            # swaps minimizes the cost!!!  

            # the len of the list, as indicated above, indicates how many times we swap in total (taking into account also the total number of qubits that are available for swapping - through swapPool)
            numPossibleSwaps = len(subsets)

            # rot seems to be a random integer, that controls the swapping and creation of the swapQBListsSwapped list 
            # why is it -2? That's because we want to assign an equal probability for all permutations, and rot = 0 achieves the same permutation as rot = swapQBnum 

            '''
            I just altered this from -2 to -1 !!!
            This has to go later, in the end the swapPool cannot have size 0! This just cannot be -> debug 
            '''
            if swapQBnum > 1: 
                # rot == 0 is not allowed, we *have* to swap the qubits. i guess...
                rot = random.randint(1, swapQBnum-1)
                # rot = 1
            else: 
                rot = 0 # random.randint(0, 0)

            # here, we create the actual list of qubits that shall be swapped. 
            # using the example above, lets assume we already picked qubit 4 to be swapped: 
            # swapQBLists = [[4] + list((1,2)), [4] + list((1,3)) + [4] + list((2,3))] = [[4,1,2], [4,1,3], [4,2,3]]
            swapQBLists = [[q1] + list(subset) for subset in subsets]

            # for every element in this swapQBList we iterate over all the sublists and do: 
            # swapQBListsSwapped = [4,1,2][rot:] + [4,1,2][:rot]
            # Let's assume rot = 1
            # swapQBListsSwapped = [1,2] + [4] = [1,2,4]
            # What is effectively done is, the qubits in the list are permuted by a random factor 
            # (here, it is clear why we chose -2 above; rot = 0 and rot = 2 would achieve exactly the same swapQBListsSwapped)
            swapQBListsSwapped = [swapQBLists[ssi][rot:] + swapQBLists[ssi][:rot] for ssi in range(len(swapQBLists))]


        # In case we want to exchange whole processing zones / and still can 
        else: 

            # I guess, if there is only one processing zone, we can skip this step 
            if Mmax > 1: 

                # swap two entire processing zones 
                swapProcessingZones = True 

                # increase this, obviously 
                numProcessingZoneSwaps += 1 

                # we want to swap two processing zones, choose 2 numbers from all the processing zones, processingZonesSwap is a list  
                processingZonesSwap = random.sample(range(Mmax), 2)

                # get all the qubits in the two processing zone numbers of the processing zones to be exchanged 
                # remember: QBTbl = [q for q in range(Nq)] = [1,2,3,4,5,6,...,Nq]
                # qubits corresponding to number of first processing zone 
                processingZone1 = [q for q in QBTbl if s1Tbl[step][q] == "p" and zonesTbl[step][q] == processingZonesSwap[0]]

                # qubits corresponding to number of second processing zone 
                processingZone2 = [q for q in QBTbl if s1Tbl[step][q] == "p" and zonesTbl[step][q] == processingZonesSwap[1]]

                # The list now contains two elements, the two qubit lists 
                swapQBLists = [processingZone1 + processingZone2]

                # Also, the list in other direction 
                swapQBListsSwapped = [processingZone2 + processingZone1]

                # swapQBLists = [[q1, q2, ...]], so: 
                # swapQBnum is the number of qubits that have to change their position due to swapping with some partner 
                swapQBnum = len(swapQBLists[0])

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
        deltaCostBestLocal = 1000000 

        '''
        Get Y lists 
        '''

        # get the Y list corresponding to this particular block 
        Yc = Y[step]

        # if there's a block to the left, define the corresponding Y list 
        if step > 1: 
            Yp = Y[step-1]

        # if not, dont define it. 
        else: 
            Yp = [0] * Nq

        # if there's a block to the right, define the corresponding Y list 
        if step < numSteps-1: 
            Yf = Y[step + 1]

        # if not, dont 
        else: 
            Yf = [0] * Nq

        # What we do here is the following: 
        # we take the Y positions corresponding to the qubits that we want to exchange (in case of complete processing zones, exchange all of the qubits in the processing zones)
        # We calculate 2* (to be swapped qubits in left processing block + to be swapped qubits in right processing block) * (qubits in this processing block - qubits in this processing block, but swapped )

        # I guess this is a list of len (numpossibleswaps) and for every swap it keeps track of the decreasement of the cost that has been done 

        '''
        TRY THIS FOR NOW!!!
        '''


        # I added this np.array() stuff, not believing that would work but apparently, it did 
        deltaCostTbl = [2 * np.dot(np.array(Yp)[swapQBLists[ssi]] + np.array(Yf)[swapQBLists[ssi]], np.array(Yc)[swapQBLists[ssi]] - np.array(Yc)[swapQBListsSwapped[ssi]]) for ssi in range(numPossibleSwaps)]

        # deltaCostTbl = []

        # for i in range(numPossibleSwaps):
        #     Y_np = np.array(Y)
        #     Y_original = np.array(Y)
        #     Y_np[step][swapQBLists] = Y_original[step][swapQBListsSwapped]
        #     cost_temp = computeTotalCost(Y_np, Nq)
        #     deltaCostTbl.append(cost_temp)



        # orders the costs by swaps 
        ord = np.argsort(deltaCostTbl)


        '''
        WHAT EXACTLY DOES ORD LOOK LIKE?? 
        '''


        # ordering the deltacost table to see which swap minimizes the cost 
        deltaCostTbl = np.array(deltaCostTbl)[ord]

        # orders the qubits in the swaplist corresponding to the order 
        swapQBLists = [swapQBLists[ssi] for ssi in ord]

        # Also the swapped qubits i suppose 
        swapQBListsSwapped = [swapQBListsSwapped[ssi] for ssi in ord]


        '''
        Performing the update, updating the Tabu list and all the lists corresponding to the best values 
        '''


        # if flag == false; no update will be performed, the tabu list will not be updated!! 
        # 'RESET' FLAG TO FALSE
        flag = False 

        # iterate over the number of possible swaps 
        for ssi in range(numPossibleSwaps):
               
            
            YTest = np.array(Y) 

            # for every swap, exchange the positions in the Y list corresponding to the qubits in the swapQBlist with the qubits in swapQBlistSwapped 
            # remember: swapQBList contains all qubits that will swap their partner
            # swapQBListsSwapped contains all the qubits that shall be swapped, but in the order they are to be swapped to 
            YTest[step][swapQBLists[ssi]] = YTest[step][swapQBListsSwapped[ssi]]

            # 
            memberQqueries += 1

            # if this particular Y arrangement, which we obtained after swapping, is in the tabu list, so it is not allowed, continue and increase the tabu counter 
            # if YTest in TSList:
            #     tabuCtr += 1 

            #     # jump to next swap 
            #     continue 

            if np.any(np.all(YTest == TSList)):
            # if YTest in TSList:
                tabuCtr += 1 

                # jump to next swap 
                continue 

            # if not in tabu list update best local cost, set update flag true and save swapped arrangement 
            # an update shall be performed later 
            flag = True 

            # deltacostbestlocal can be worse than the best cost so far. 
            # We did not check for the quality of the cost yet. 
            deltaCostBestLocal = deltaCostTbl[ssi]

            # save corresponding Y  
            YBestUpdate = YTest

            # save corresponding processing zone constellation 
            zonesTblBestUpdate = np.array(zonesTbl)

            # save s1, s2 tables 
            s1TblBestUpdate = np.array(s1Tbl)
            s2TblBestUpdate = np.array(s2Tbl)

            # and swap zones and s1. 
            # s2 unaffected 
            zonesTblBestUpdate[step][swapQBLists[ssi]] = zonesTblBestUpdate[step][swapQBListsSwapped[ssi]]
            s1TblBestUpdate[step][swapQBLists[ssi]] = s1TblBestUpdate[step][swapQBListsSwapped[ssi]]


            # I guess greedyspread means more than one swap at a time 
            if greedySpread == False:
                break

            '''
            Greedy Search:

            Try to update arrangement on blocks left and right of the current block 
            '''

            # define this for the while-loop 
            # start with block on the right of current block 
            stepp = step + 1 

            # while we did not reach the number of processing blocks 
            # iterate over all the layers that are on the right of the current block 
            while stepp < numSteps - 1: 
                
                # I do not understand this. 
                # if the qubits that shall be swapped in the step layer do not have the same nature ('a' or 'i') in the next layer, break 
                # also, if these two sets of qubits are in different processing zones, break 
                if s2Tbl[step][swapQBLists[ssi]] != s2Tbl[stepp][swapQBLists[ssi]] or  zonesTbl[step][swapQBLists[ssi]] != zonesTbl[stepp][swapQBLists[ssi]]:
                    break

                # update the Y lists as well 
                Yc = YBestUpdate[stepp]
                Yp = YBestUpdate[stepp - 1]
              
                # if there's a right neighbour, do the same 
                if stepp < numSteps: 
                    Yf = YBestUpdate[stepp + 1]
                else: 
                    Yf = [0] * Nq
              
                # same as above 
                deltaCost2 = 2 * (Yp[swapQBLists[ssi]] + Yf[swapQBLists[ssi]]) * (Yc[swapQBLists[ssi]] - Yc[swapQBListsSwapped[ssi]])
              
                # update the best lists for stepp!! as well. We did it for step above, but now also for stepp
                if deltaCost2 < 0: 
                    deltaCostBestLocal += deltaCost2
                
                    YBestUpdate[stepp][swapQBLists[ssi]] = YBestUpdate[stepp][swapQBListsSwapped[ssi]]
                
                    zonesTblBestUpdate[stepp][swapQBLists[ssi]] = zonesTblBestUpdate[stepp][swapQBListsSwapped[ssi]]
                    s1TblBestUpdate[stepp][swapQBLists[ssi]] = s1TblBestUpdate[stepp][swapQBListsSwapped[ssi]]
                
                    for sqbi in range(swapQBLists[ssi]): 
                        sqb = swapQBLists[ssi][sqbi]
                 
                    if s1TblBestUpdate[stepp][sqb] == "i" and s2TblBestUpdate[stepp][sqb] == "a":
                        print("  ERROR in greedy expansion, step: ", step)
                else: 
                    stepp = numSteps
                
                stepp += 1 


            # block on the left of current block 
            stepp = step - 1 

            # iterate over all the layers that are on the left of the current block 
            while stepp > 0: 


                # Muss noch geandert werden!! 


                if s2Tbl[step][swapQBLists[ssi]] != s2Tbl[step][swapQBLists[ssi]] or  zonesTbl[step][swapQBLists[ssi]] != zonesTbl[stepp][swapQBLists[ssi]]:
                    break

                Yc = YBestUpdate[stepp]
                Yp = YBestUpdate[stepp - 1]
              
                if stepp < numSteps: 
                    Yf = YBestUpdate[stepp + 1]
                else: 
                    Yf = [0] * Nq
              
                deltaCost2 = 2 * (Yp[swapQBLists[ssi]] + Yf[swapQBLists[ssi]]) * (Yc[swapQBLists[ssi]] - Yc[swapQBListsSwapped[ssi]])
              

                if deltaCost2 < 0: 
                    deltaCostBestLocal += deltaCost2
                
                    YBestUpdate[stepp][swapQBLists[ssi]] = YBestUpdate[stepp][swapQBListsSwapped[ssi]]
                
                    zonesTblBestUpdate[stepp][swapQBLists[ssi]] = zonesTblBestUpdate[stepp][swapQBListsSwapped[ssi]]
                    s1TblBestUpdate[stepp][swapQBLists[ssi]] = s1TblBestUpdate[stepp][swapQBListsSwapped[ssi]]
                
                    for sqbi in range(swapQBLists[ssi]): 
                        sqb = swapQBLists[ssi][sqbi]
                 
                    if s1TblBestUpdate[stepp][sqb] == "i" and s2TblBestUpdate[stepp][sqb] == "a":
                        print("  ERROR in greedy expansion, step: ", step)
                else: 
                    stepp = 1
                
                stepp -= 1 

            # this loop is breaked here:  for ssi in range(numPossibleSwaps)
            # we do not iterate over the possible swaps anymore. In the algorithm, now we deal with what comes after the swapping, all the swapping is finished. Now, for the updating 
            break  

        '''
        Swapping is finished -> Updating 
        '''

        # no update if flag == false
        # if flag == false, this means that the step we meant to perform was tabu 
        if flag == False: 
            noUpdateCtr += 1 

        # if flag == true, update tabu list and all the best lists, and ggf bestcost 
        if flag == True: 

            # assign this Y to the corresponding element in the tabu list, why not just use append? 
            TSList[TSFill] = YBestUpdate

            # increase counter by one 
            TSFill += 1

            # when we have reached the end of the tabu list: start filling the tabu list, starting at the oldest - the first - element again 
            if TSFill >= TSlen: 
                TSFill = 0

            # updateY
            Y = YBestUpdate 

            # update zones
            zonesTbl = zonesTblBestUpdate

            # update s1, s2 
            s1Tbl = s1TblBestUpdate
            s2Tbl = s2TblBestUpdate

            # update total cost 
            costTot += deltaCostBestLocal

            # if, globally, cost is minimal: 
            if costTot < costBest: 

                # global best cost is current cost 
                costBest = costTot 

                # and all the other best lists get updated too 
                YBest = YBestUpdate
                zonesTblBest = zonesTblBestUpdate
                s1TblBest = s1TblBestUpdate
                s2TblBest = s2TblBestUpdate

                # increase counter, because right now we have improved the cost!
                numImprovements += 1 

                # if we want to store all of the improvements on b that are made in the course of this algorithm 
                if storeAllBestBP == True: 

                    # save it by reconstructing the blocks, given the old BP as well as the Y, optimized by the tabu search 
                    bNew = reconstructBlocksFromArrangements(BP, Fsizes, Qmax, Mmax, Nq, YBest, zonesTblBest, s1TblBest, s2TblBest)

                # Taking care of some counters 
                if swapProcessingZones == False: 
                    if swapQBnum > 2: 
                        numImprovementMultiSwaps += 1 

                    else: 
                        numImprovementTwoSwaps += 1

                if swapProcessingZones == True:
                    numImprovementProcessingZonesSwaps += 1

            # if we did not improve upon the best cost yet, set local delta cost to zero 
            else: 
                deltaCostBestLocal = 0 

        # take care of the two cost tables
        costProgressTbl[i] = [i, costTot]
        bestCostProgressTbl[i] = [i, costBest]



    # here is still a lot missing for I guess graphic and debugging purposes, first I have to try to understand this algorithm 

    '''
    All done 
    '''

    return bNew, costProgressTbl, bestCostProgressTbl, YBest, numImprovements, tabuCtr, noUpdateCtr
            

bNew, costProgressTbl, bestCostProgressTbl, YBest, numImprovements, tabuCtr, noUpdateCtr = improvePlacementTabuSearch(processingBlockListAfterOptimizing, FSIZES, QMAX, MMAX, NQ, TSiterations=600, TSlen=30, swapNumMax=3, processingZoneSwapFraction=0, greedySpread=False, storeAllBestBP=True, echo=True)

'''
Plotting cost evolution
'''

cost_list = []
for i in range(1, len(costProgressTbl)):
    cost_list.append(costProgressTbl[i][1])

best_cost_list = []
for i in range(1, len(bestCostProgressTbl)):
    best_cost_list.append(bestCostProgressTbl[i][1])

title = str(numImprovements) + '#tabus: ' + str(tabuCtr) + '#noUpdates: ' + str(noUpdateCtr)

# plt.figure()
# plt.plot(cost_list, label = 'cost')
# plt.plot(best_cost_list, label = 'best cost')
# plt.title('Evolution of the cost with the iterations, #impr: ' + title + '\n')
# plt.xlabel('Iterations')
# plt.ylabel('Cost')
# plt.legend()
# plt.show()

# print('B is: \n', B)
# print('bNew is: \n', bNew)

# visualize_blocks(bNew, 'After Tabu Search, cost: ' + str(computeTotalCost(YBest, NQ)))



'''
Tabu Search over. 
Now, for the alternating optimization.

'''

print('OPTIMIZING EVERYTING')


def optimizeArrangements(BP, Nq, Fsizes, Qmax, Mmax, numOptimizationSteps, TSiterations, TSlen, echo, visualOutput):
    '''
    In this function, the deterministic and the tabu search algorithm are applied to a set of processing blocks B in an alternating manner. 
    First, the deterministic algorithm is applied, then the tabu search. This scheme is repeated numOptimizationSteps times. 

    Given: 
        BP:                     List of processing blocks 
        numOptimizationSteps:   Number of iterations for the alternating algorithm 
        TSiterations:           Number of iterations for the tabu search 
        TSlen:                  Length of the tabu list
    Returns: 
        bNew:                   The one constellation of qubits in processing blocks that minimizes the total cost
        costList:               Evoluation of the cost over the iterations of the alternating algorithm
    '''
    bNew = BP

    # keeps track of the total best cost 
    totalBestCostTbl = [[] for _ in range(2 * numOptimizationSteps)]

    # 
    grPtbl = [[] for _ in range(2 * numOptimizationSteps)]

    # 
    grPBest = []

    # list of Y positions to start with 
    YTemp = computeArrangements(bNew, Fsizes, Qmax)

    # total cost to start with, to be minimized 
    costTotInitial = computeTotalCost(YTemp, Nq)

    # high number, why not initial? 
    costTotBest = 10 ** 9 

    costList = []
    BList = []

    # iterate over the number of Optimizing steps, given the function as argument 
    for optimizationstep in range(numOptimizationSteps): 

        print('total cost 0, iteration ', optimizationstep, 'cost is: ', computeTotalCost(computeArrangements(bNew, Fsizes, Qmax), Nq))

        # deterministic algorithm, returns updated bNew 
        bNew, tempListUnimportant = improvePlacement(bNew, Nq, Fsizes, Qmax, Mmax, False)

        print('total cost 1, iteration ', optimizationstep, 'cost is: ', computeTotalCost(computeArrangements(bNew, Fsizes, Qmax), Nq))


        if echo == True: 
            print('echo')

        if visualOutput == True:
            print('visualoutput')

        # Tabu Search algorithm, returns updatet bNew!
        bNew, costProgressTbl, bestCostProgressTbl, YBest, numImprovements, tabuCtr, noUpdateCtr = improvePlacementTabuSearch(bNew, Fsizes, Qmax, Mmax, Nq, TSiterations, TSlen, 3, 0, greedySpread = False, storeAllBestBP= True, echo = False)

        print('total cost 2, iteration ', optimizationstep, 'cost is: ', computeTotalCost(computeArrangements(bNew, Fsizes, Qmax), Nq))

        costList.append(computeTotalCost(computeArrangements(bNew, Fsizes, Qmax), Nq))
        BList.append(copy.deepcopy(bNew))

        if echo == True: 
            print('echo')

        if visualOutput == True: 
            print('visualoutput')

        # still needs to be returned by tabusearch 
        # if the minimal cost obtained by the tabu search is smaller than the best cost so far, replace the best cost with the Tabu Search one. 
        # if bestCostUpdateAll[-1] < costTotBest:

        #     if visualOutput == True: 
        #         print('visualoutput')

        #     # last element in list 
        #     costTotBest = bestCostUpdateAll[-1]

    # get the B list for which the cost is minimal, argsort sorts from lowest to highest 
    costIndices = np.argsort(costList)
    BList = np.array(BList)
    BList = BList[costIndices]

    # this gets flattened in the mathematica code 
    grPtbl = grPtbl 

    # this as well 
    totalBestCostTbl = totalBestCostTbl


    # 
    return grPBest, costTotBest, grPtbl, totalBestCostTbl, costList, BList[0]
 

a,b,c,d,costEvolution, bNew = optimizeArrangements(processingBlockList, NQ, FSIZES, QMAX, MMAX, numOptimizationSteps= 10, TSiterations= 10000, TSlen= 100, echo = True, visualOutput = False)


visualize_blocks(processingBlockList, 'Processing block arrangement before optimization, cost: ' + str(computeTotalCost(computeArrangements(processingBlockList, FSIZES, QMAX), NQ)))



visualize_blocks(bNew, 'After alternating search, cost: ' + str(computeTotalCost(computeArrangements(bNew, FSIZES, QMAX), NQ)))


plt.figure()
plt.plot(costEvolution, label = 'cost')
plt.title('Evolution of total cost with alternating iterations \n')
plt.xlabel('Iterations')
plt.ylabel('Cost')
plt.legend()
plt.show()


'''
Alternating algorithm over 

Now, the displaying shall be done. 
'''



# show_layeredCircuit(10, circuit_of_qubits, layeredcircuit)
# show_circuit_after_optimizing(bNew, 10, circuit_of_qubits)