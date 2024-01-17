from RandomCircuitQiskit import *

from itertools import product 

# create a random circuit 
randomCircuit, gatesList, listOfTempCircuits = CreateRandomCircuit(5, 5, 2, False)


class RandomCircuit:

    def __init__(self, nQ, nGates):
        self.nQ = nQ
        self.nGates = nGates
        self.circuit, self.gatesList, self.listOfTempCircuits = self.CreateRandomCircuit(nQ, nGates, 2, False)
        self.allPossibleArrangements = []
        self.allPossibleArrangements.append(self.gatesList)
        # for displaying purposes 
        self.commutationMatrix = np.zeros((self.nGates, self.nGates))

        # for finding all possible arrangements later 
        self.globalTabuList = []

        # collect all possible arrangements 
        self.listOfPossiblePerms = []


    # necessary for later
    def CheckCommutation(self, matrixOne, matrixTwo): 

        resultOne = np.matmul(matrixOne, matrixTwo)

        resultTwo = np.matmul(matrixTwo, matrixOne)

        # if resultOne == resultTwo: 
        if np.array_equal(resultOne, resultTwo):
            return True 
        else: 
            return False 



    def CountGates(self, qc: QuantumCircuit): 
        '''
        This function counts the gates in a circuit
        '''
        gateCount = {qubit: 0 for qubit in qc.qubits}
        for gate in qc.data: 
            for qubit in gate.qubits: 
                gateCount[qubit] += 1 
        
        return gateCount



    def RemoveUnusedQubits(self, qc: QuantumCircuit):
        '''
        This function removes qubits from a circuit that are unused. 
        We will need this function when investigating the commutation behaviour between gates
        '''
        gateCount = CountGates(qc)
        for qubit, count in gateCount.items():
            if count == 0: 
                qc.qubits.remove(qubit)
        
        return qc



    def CreateRandomCircuit(self, nQubits, nGates, maxNumberOperations, display):
        '''
        this function does three things: 
        1. it creates a random qiskit circuit and
        2. a corresponding gateslist and 
        3. the corresponding commutation matrix 

        '''

        # first, create one circuit with only one gate 
        circuitToBeAltered, involvedQubits = randomCircuitTwoQubits(nQubits, 1, maxNumberOperations, measure=False)

        if nGates < 1:
            print('Error, number of gates smaller than one.')
            return 

        # print(circuitToBeAltered)

        gatesList = [[0, involvedQubits]]


        listOfTempCircuits = [circuitToBeAltered]

        # iterate over gates that we are going to create
        for iGate in range(nGates-1):

            # if we reached the last gate, we do want to measure 
            if iGate == nGates -2:
                # was true before, but problems with matrix representation 
                tempCirc, involvedQubits = randomCircuitTwoQubits(nQubits, 1, maxNumberOperations, measure=False)
            else:
                tempCirc, involvedQubits = randomCircuitTwoQubits(nQubits, 1, maxNumberOperations, measure=False)


            # collect the tempcircuits to reason about commutation behaviour later 
            listOfTempCircuits.append(tempCirc)



            # At this point, we created the temporary circuit. Now we want to check if it commutes with the other circuits that we have seen. 
            gatesList.append([iGate+1, involvedQubits])
            
            # add barrier to the main circuit, then add the temporary circuit
            # circuitToBeAltered.barrier()
            circuitToBeAltered = circuitToBeAltered.compose(tempCirc)
        

        if display: 
            circuitToBeAltered.draw(output='mpl')

            plt.show()

            print(circuitToBeAltered)

        return circuitToBeAltered, gatesList, listOfTempCircuits


    def DoGatesCommute(self, gateOne, gateTwo):
        '''
        gateOne = is a number
        gateTwo = is a number 
        listOfTempCircuits = list of the gates that make up the circuit

        returns a boolean indicating if the two gates commute or not 
        '''

        q1, q2              = self.gatesList[gateOne][1]
        otherQ1, otherQ2    = self.gatesList[gateTwo][1]


        # create two circuits based on the gates circuit representation (stored in tempcircuitList) 
        # and see if the corresponding matrices commute
        circuit1 = self.listOfTempCircuits[gateOne]
        circuit2 = self.listOfTempCircuits[gateTwo]

        # the circuits now consist of two qubits each
        circuit1 = RemoveUnusedQubits(circuit1)
        circuit2 = RemoveUnusedQubits(circuit2)

        testCircuit = QuantumCircuit(3)

        # create a circuit with three qubits with both of the gates 
        if q1 == otherQ1: 
            circuit1 = testCircuit.compose(circuit1, [0, 2])
            circuit2 = testCircuit.compose(circuit2, [0, 1])
        
        elif q2 == otherQ2: 
            circuit1 = testCircuit.compose(circuit1, [0, 2])
            circuit2 = testCircuit.compose(circuit2, [1, 2])

        elif q1 == otherQ2: 
            circuit1 = testCircuit.compose(circuit1, [1, 2])
            circuit2 = testCircuit.compose(circuit2, [0, 1])

        elif q2 == otherQ1: 
            circuit1 = testCircuit.compose(circuit1, [0, 1])
            circuit2 = testCircuit.compose(circuit2, [1, 2])

        # if the two circuits do not share any qubits, just continue. They will certainly commute 
        # BUT: we do not set the indices of the commuationmatrix to one here. The commutationmatrix should tell us the commutation behaviour between 
        # gates that are not obvious - such gates that share qubits!!
        else: 
            return False  

        
        # get matrix representation of circuit 1
        backend = Aer.get_backend('unitary_simulator')
        job = execute(circuit1, backend)
        result = job.result()

        circuit1Matrix = result.get_unitary(circuit1, decimals = 3)

        # get matrix representation of circuit 2
        backend = Aer.get_backend('unitary_simulator')
        job = execute(circuit2, backend)
        result = job.result()

        circuit2Matrix = result.get_unitary(circuit2, decimals = 3)


        if CheckCommutation(circuit1Matrix, circuit2Matrix): 
            print('These Gates commute! gates: ', gateOne, gateTwo)
            return True

        else:
            return False 


    def CreateCommutationMatrix(self): 
        '''
        Way of displaying the commutation behaviour between all the involved gates
        This function creates a matrix indicating if gate i and j commute. 
        If so -> matrix[i,j] = 1, else matrix[i,j] = 0
        It also plots the matrix as a heatmap
        '''

        self.commutationMatrix = np.zeros((self.nGates, self.nGates))
        for gateNo in range(len(self.gatesList)):

            for otherGateNo in range(len(self.gatesList)):

                if gateNo >= otherGateNo: 
                    continue
            
                if self.DoGatesCommute(gateNo, otherGateNo): 
                    self.commutationMatrix[gateNo][otherGateNo] = 1
                    self.commutationMatrix[otherGateNo][gateNo] = 1

        import seaborn as sns

        sns.heatmap(self.commutationMatrix, annot=False, cmap='binary')

        # array to display neighbours 
        testArray = np.zeros((self.nGates, self.nGates))

        for i in range(self.nGates): 
            for j in range(self.nGates):
                if i == j+1 or j == i+1: 
                    testArray[i, j] = 1

        # Add labels and title
        plt.xlabel('Gate no.')
        plt.ylabel('Gate no.')
        plt.title('Commutation Matrix')

        sns.heatmap(testArray, annot=False, cmap='binary', alpha = 0.2, cbar=False)

        plt.show()


    def SwapGates(self, tempArrangement, gateOne, gateTwo): 
        tempList = copy.deepcopy(tempArrangement)

        # swap the gates
        tempList[gateOne], tempList[gateTwo] = tempList[gateTwo], tempList[gateOne]

        return tempList



    def FindAllPermutations(self, providedList):
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
        self.BFScount += 1

        for tempGatesList in providedList: 

            # this list contains all possible permutations of gates (all possible circuits)
            listOfPossiblePermutations = []

            # this list contains all of the gates that can be swapped with each other in the format 
            # [[g1,g2], [g3,g4], ...]
            possibleSwaps = []

            # if this list is in the tabu list already, go on 
            if tempGatesList in self.globalTabuList: 
                continue

            # if not, we now append it to it
            self.globalTabuList.append(tempGatesList)

            # self.listOfPossiblePerms.append(tempGatesList)

            
            # make another list without the qubits 
            gatesList = [gate[0] for gate in tempGatesList]

            # iterate over all possible gates and check if gates commute with their immediate neighbours 
            for gateNo in range(len(gatesList)): 
                
                # python indexing, that's why the '-1'
                gate = gatesList[gateNo]

                # if gateNo == len(gatesList) - 1 -> break *and* here we compare gate to gate+1
                if gateNo >= len(gatesList)-2:
                    continue 

                otherGate = gatesList[gateNo + 1]


                if self.DoGatesCommute(gate, otherGate):
                    self.commutationMatrix[gate-1][gate] = 1
                    possibleSwaps.append([gate, otherGate])

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
            # for swapNo in range(len(possibleSwaps)): 
            #     swap = possibleSwaps[swapNo]
            #     g1 = swap[0]
            #     for otherSwapNo in range(len(possibleSwaps)): 

            #         otherSwap = possibleSwaps[otherSwapNo]
            #         if g1 == otherSwap[0] or g1 == otherSwap[1]: 
            #             for perm in all_permutations:
            #                 if perm[swapNo]==1 and perm[otherSwapNo] ==1: 
            #                     all_permutations.remove(perm)


            # if there's non trivial swaps to be made  
            if len(all_permutations) > 1:

                for perm in all_permutations:
                    tempArrangement = copy.deepcopy(self.gatesList)

                    for i in range(len(perm)): 
                        
                        if perm[i] == 1: 
                            tempArrangement = self.SwapGates(tempArrangement, possibleSwaps[i][0], possibleSwaps[i][1])
                    
                    if tempArrangement not in self.globalTabuList:  

                        print('Arrangement not in Tabu list')   
                        listOfPossiblePermutations.append(tempArrangement)
                        # self.listOfPossiblePerms.append(tempArrangement)
                    else: 

                        print('Arrangement in Tabu list')
                        continue


            # now we created all possible arrangements
            self.FindAllPermutations(listOfPossiblePermutations)
                
            return 

    def FindAllPossibleArrangements(self):
        self.BFScount = 0
        # self.listOfPossiblePerms.append(self.gatesList)
        self.FindAllPermutations([self.gatesList])
        print(self.globalTabuList)



randomCirc = RandomCircuit(5, 5)

print(randomCirc.circuit)

randomCirc.FindAllPossibleArrangements()

# randomCirc.CreateCommutationMatrix()