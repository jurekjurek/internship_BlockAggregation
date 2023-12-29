from BlockAggregation import *

'''
In this file, the gatecoverage and thus, the cost of the inital arrangements is compared for the different commutations of the inital random circuit
that are allowed as calculated in the file RandomCircuitQiskit.py

Two things will be displayed: 
    The gatecoverage for the different arrangements 
    The cost of the resulting qubit arregations
'''


def CompareDifferentArrangements(show):
    # create the randomcircuits and the corresponding list of possible arrangements 
    gatesList, commutationMatrix = CreateRandomCircuit(NQ, GATES, 2, display= False)
    possibleArrangements = BFS([gatesList], commutationMatrix)

    if show: 
        ShowCommutationMatrix(commutationMatrix)

    if len(possibleArrangements) == 1: 
        # print('Only one variation found. No other arrangements due to commutation.')
        return [0, 1]

    # else: 
    #     print('Number of variations found: ', len(possibleArrangements))
    # 
    costList = []
    gateCoverageList = []
    for i in range(len(possibleArrangements)):
        tempCircuit = possibleArrangements[i]
        tempArrangement = blockProcessCircuit(tempCircuit, NQ, FSIZES, QMAX, MMAX)

        if show == True: 
            visualize_blocks(tempArrangement, 'Arrangement after Block Aggregation number ' + str(i))
        costList.append(computeTotalCost(computeArrangements(tempArrangement, FSIZES, MMAX), NQ))

        a, b, c, tempGateCoverage = AggregateBlocksStep(tempCircuit, NQ, QMAX, MMAX)
        gateCoverageList.append(tempGateCoverage)

        


    if show == True:
        plt.plot(costList)
        plt.xlabel('Commutation variation No.')
        plt.ylabel('Cost')
        plt.title('Cost over the different possible arrangements, max diff: ' + str(max(costList) - min(costList)))
        plt.show()

        plt.plot(gateCoverageList)
        plt.xlabel('Commutation variation No.')
        plt.ylabel('Gate Coverage')
        plt.title('Gate Coverage over different possible Arrangements')
        plt.show()

    # costlist[0] corresponds to the initial element that would have been chosen if no commutation had been considered
    return [max(costList) - costList[0], len(possibleArrangements)]

numberOfIterations = 500
storingList = []
for iteration in range(numberOfIterations): 
    if iteration % 10 == 0:
        print(iteration)
    storingList.append( CompareDifferentArrangements(False) )

# average improvement over iterations, considering all cases: 
count = 0 
for i in range(len(storingList)): 

    count += storingList[i][0]

print('Average improvement for all:')
print(count/len(storingList))

tabuList = []

avgList = []
indexList = []

indexCount = np.zeros(50)

for i in range(len(storingList)): 
    
    tempIndex = storingList[i][1]

    print(tempIndex)


    if tempIndex < 50: 
        indexCount[tempIndex-1] += 1

    # we only want to average over 5 values maximum for each variable 
    if tempIndex in tabuList or tempIndex == 1:# or indexCount[tempIndex] > 5: 
        if tempIndex == 1: 
            indexCount[0] += 1
        continue

    tabuList.append(tempIndex)

    tempCount = 0
    tempSum = 0



    for j in range(len(storingList)): 
        if storingList[j][1] == tempIndex: 
            tempSum += storingList[j][0]
            tempCount += 1

    avgList.append(tempSum / tempCount)
    indexList.append(tempIndex)


    print('Average for possiblearrangements Length ', tempIndex, ' is ', tempSum / tempCount, '. \n Where the number of averages was ', tempCount)


tempBins = range(1, 51)
# print(tempBins)

xValues = np.arange(50)

print(indexCount)
plt.bar(xValues, indexCount)
plt.xlim(-1, 10.5)
plt.title('Histogram')
plt.ylabel('Frequency')
plt.xlabel('Number of possible arrangements')
plt.show()

plt.title('Average cost improvement for different arrangements')
plt.scatter(indexList, avgList)
plt.xlim(0,50)
plt.xlabel('Numbers of possible arrangements')
plt.ylabel('Average Cost Improvement')
plt.show()