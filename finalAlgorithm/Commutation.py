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

        testArray = np.zeros((40, 40))

        for i in range(40): 
            for j in range(40):
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





randomCirc = RandomCircuit(5, 5)

print(randomCirc.circuit)

randomCirc.FindAllPossibleArrangements()

randomCirc.CreateCommutationMatrix()