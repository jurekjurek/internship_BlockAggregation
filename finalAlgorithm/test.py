# test the algorithm for finding the different arrangements in commutation.py

from itertools import product 
import numpy as np

def FindAllPermutations(self, tempGatesList):

    self.BFScount += 1
    listOfPossiblePermutations = []
    possibleSwaps = []

    

    # make another list without the qubits 
    gatesList = [gate[0] for gate in tempGatesList]

    for gateNo in range(len(gatesList)): 
        
        # python indexing, that's why the '-1'
        gate = gatesList[gateNo]

        if gateNo >= len(gatesList)-2:
            break 


        if self.DoGatesCommute(gate, gate+1):
            self.commutationMatrix[gate-1][gate] = 1
            possibleSwaps.append([gate, gate+1])

    print(listOfPossiblePermutations)

    # 
    possible_values = [0, 1]

    # Generate all permutations
    all_permutations = list(product(possible_values, repeat=len(possibleSwaps)))

    print(all_permutations)

    for perm in all_permutations:
        tempArrangement = copy.deepcopy(self.gatesList)

        for i in range(len(perm)): 
            
            if perm[i] == 1: 
                tempArrangement = self.SwapGates(tempArrangement, possibleSwaps[i][0], possibleSwaps[i][1])
            
        listOfPossiblePermutations.append(tempArrangement)

    # check all following commutations: 
    # gate i with gate i+2, gate i+1 with gate i-1
    for i in range(len(possibleSwaps)):
        tempGateOne = possibleSwaps[i][0]
        tempGateTwo = possibleSwaps[i][1]

        # if list index out of range, just continue 
        if (tempGateOne + self.BFScount) >= len(gatesList) or tempGateTwo <= self.BFScount: 
            continue            

        if self.DoGatesCommute(tempGateOne, tempGateOne + self.BFScount + 1):
            self.commutationMatrix[tempGateOne-1][tempGateOne + self.BFScount] = 1 
        if self.DoGatesCommute(tempGateTwo - self.BFScount - 1, tempGateTwo):
            self.commutationMatrix[tempGateTwo - self.BFScount - 2][tempGateTwo-1] = 1


    # update the global list of all possible permutations 
    for i in range(len(listOfPossiblePermutations)): 
        print('Possible Arrangements: ', listOfPossiblePermutations[i])

        if listOfPossiblePermutations[i] not in self.allPossibleArrangements: 
            self.allPossibleArrangements.append(listOfPossiblePermutations[i])

            thisPerm = all_permutations[i]
            involvedGates = []
            for j in range(len(thisPerm)): 
                if j == 1: 
                    involvedGates.append(possibleSwaps[j])


            # only if the next neighbour also commutes, look at it 
            # tempGateOne = possibleSwaps[i][0]
            # tempGateTwo = possibleSwaps[i][1]
            # if 
            # if (tempGateOne - 1) > len(gatesList) - self.BFScount or tempGateTwo <= self.BFScount: 
            #     continue
            # if self.DoGatesCommute(tempGateOne, tempGateOne+ self.BFScount) or self.DoGatesCommute(tempGateTwo - self.BFScount, tempGateTwo):
            #     

            # if the commutationmatrix for the corresponding gates is == 1, we consider this case. Otherwise we do not. 

            for involvedGate in involvedGates: 
                tempGateOne = involvedGate[0]
                tempGateTwo = involvedGate[1]

                if (tempGateOne + self.BFScount) >= len(gatesList) or tempGateTwo <= self.BFScount: 
                    continue  

                if self.commutationMatrix[tempGateOne-1][tempGateOne+self.BFScount] == 1 or self.commutationMatrix[tempGateTwo-self.BFScount-2][tempGateTwo-1] == 1:
                    self.FindAllPermutations(listOfPossiblePermutations[i])



def FindAllPossibleArrangements(self):
    self.BFScount = 0
    self.FindAllPermutations(self.gatesList)