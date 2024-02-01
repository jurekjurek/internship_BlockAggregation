import numpy as np
from RandomCircuitQiskit import *

from itertools import product 

globalTabuList = []
gatesList = [[1, [1,2]], [2, [3,4]], [3, [5, 6]], [4, [7, 8]], [5, [9, 10]]]

listOfPossiblePerms = []

commutationMatrix = np.zeros((5,5))

commutationMatrix[1, 2] = 1 
commutationMatrix[2, 1] = 1 
commutationMatrix[2, 3] = 1 
commutationMatrix[3, 2] = 1 
commutationMatrix[0, 3] = 1
commutationMatrix[3, 0] = 1
commutationMatrix[1, 3] = 1
commutationMatrix[3, 1] = 1


def FindAllPermutations(providedList):
    '''
    This function finds, given a list of gates in a circuit, all possible arrangements of these gates (all possible circuits) based on the commutation 
    behaviours of these gates relative to each other. 
    Consider the gates in the circuit [1,2,3,4,5] and consider that [1,2], [4,5] and [1,3] commute. 
    The possible arrangements of this circuit then are: 
    [1,2,3,4,5]
    [1,2,3,5,4]
    [2,1,3,4,5]
    [2,1,3,5,4]
    and 
    [2,3,1,4,5]
    [2,3,1,5,4]
    The algorithm works like this: We check if immediate neighbours commute (in this case 4,5 and 1,2). If this is the case, we create the resulting possible
    arrangements due to this commutation (the first 4 - or in general 2^(numberOfPossibleSwaps) (2 because each swap can either be true or false - 
    executed or not executed))

    '''

    # set to =0 in the FindAllArrangements 
    # everytime this function is called, the counter is increased by one

    for tempGatesList in providedList: 

        # this list contains all possible permutations of gates (all possible circuits)
        listOfPossiblePermutations = []

        # this list contains all of the gates that can be swapped with each other in the format 
        # [[g1,g2], [g3,g4], ...]
        possibleSwaps = []

        # if this list is in the tabu list already, go on 
        if tempGatesList in globalTabuList: 
            continue

        # if not, we now append it to it
        globalTabuList.append(tempGatesList)

        # self.listOfPossiblePerms.append(tempGatesList)

        
        # make another list without the qubits 
        gatesList = [itGate[0] for itGate in tempGatesList]

        # iterate over all possible gates and check if gates commute with their immediate neighbours 
        for gateNo in range(len(gatesList) - 1): 
            
            # python indexing, that's why the '-1'
            gate = gatesList[gateNo] - 1

            otherGate = gatesList[gateNo + 1] - 1

            print(gate, otherGate)

            if commutationMatrix[gate, otherGate] == 1:

                print('These gates commute ', gate, ' ', otherGate)

                # we do not collect the gates themselves but the indices of the respective gates in the temporary list! 
                possibleSwaps.append([gateNo, gateNo+1])

        # works 
        print(listOfPossiblePermutations)

        # generate all possible permuations of exchanging the n possible gate swaps (that are independent of each other for now)
        possible_values = [0, 1]

        # but, one thing we still have to check is that the gates are really independent of each other 
        # because if, e.g., possibleSwaps = [[1,4], [8,9], [4,2]]
        # we have a problem because swap 1 and 3 cannot be executed at the same time! look further downstairs


        # Generate all permutations, this is a list of lists of 0s and 1s 
        # each list corresponds to one permutation; this list: 
        # [[...], ..., [1,0,0,1,0], [...], ....]
        # e.g. means that the first and fourth swaps are executed for this specific circuit 
        all_permutations = list(product(possible_values, repeat=len(possibleSwaps)))

        print('all:', all_permutations)

        print('len all perms:', len(all_permutations))

        # essentially, in these cases: we have to delete the cases from the permutation (consisting of 0s and 1s) in which 
        # both of the swaps (that are not independent of each other) are 1
        # OPTIMIZE THIS FOR SURE!
        for swapNo in range(len(possibleSwaps)): 
            swap = possibleSwaps[swapNo]
            g1 = gatesList[swap[0]]
            g2 = gatesList[swap[1]]
            for otherSwapNo in range(len(possibleSwaps)): 

                otherSwap = possibleSwaps[otherSwapNo]
                if otherSwap == swap: 
                    continue
                if g1 in otherSwap or g2 in otherSwap: 
                    for perm in all_permutations:
                        if perm[swapNo]==1 and perm[otherSwapNo] ==1: 
                            all_permutations.remove(perm)


        # if there's non trivial swaps to be made  
        if len(all_permutations) > 1:

            for perm in all_permutations:
                tempArrangement = copy.deepcopy(tempGatesList)

                for i in range(len(perm)): 
                    
                    if perm[i] == 1: 
                        tempArrangement = SwapGates(tempArrangement, possibleSwaps[i][0], possibleSwaps[i][1])

                    else:
                        continue
                
                if tempArrangement not in globalTabuList:  

                    print('Arrangement not in Tabu list')   
                    listOfPossiblePermutations.append(tempArrangement)
                    if tempArrangement not in listOfPossiblePerms: 
                        listOfPossiblePerms.append(tempArrangement)
                else: 

                    print('Arrangement in Tabu list')
                    continue


        # now we created all possible arrangements
        FindAllPermutations(listOfPossiblePermutations)
            
        return 



def SwapGates(tempArrangement, gateOne, gateTwo): 

    # gateOneNo are indices in the gatesList for which gates to switch! 
    # gateOne are the indices of the 
    # gateOne = gatesList[gateOneNo][0] - 1
    # gateTwo = gatesList[gateTwoNo][0] - 1

    tempList = copy.deepcopy(tempArrangement)

    # swap the gates
    tempList[gateOne], tempList[gateTwo] = tempList[gateTwo], tempList[gateOne]

    return tempList




def FindAllPossibleArrangements():
    listOfPossiblePerms.append(gatesList)
    FindAllPermutations([gatesList])
    for i in listOfPossiblePerms: 
        print(i)


FindAllPossibleArrangements()