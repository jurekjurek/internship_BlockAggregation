from TabuSearch import *



def optimizeArrangements(processingBlockArrangement, nQ, Fsizes, qMax, mMax, numOptimizationSteps, TSiterations, tabuListLength, echo, visualOutput, improvementFactor):
    '''
    In this function, the deterministic and the tabu search algorithm are applied to a set of processing blocks B in an alternating manner. 
    First, the deterministic algorithm is applied, then the tabu search. This scheme is repeated numOptimizationSteps times. 

    Given: 
        processingBlockArrangement:                     List of processing blocks 
        numOptimizationSteps:   Number of iterations for the alternating algorithm 
        TSiterations:           Number of iterations for the tabu search 
        tabuListLength:                  Length of the tabu list
    Returns: 
        newProcessingBlockArrangement:                   The one constellation of qubits in processing blocks that minimizes the total cost
        costList:               Evoluation of the cost over the iterations of the alternating algorithm
    '''
    newProcessingBlockArrangement = processingBlockArrangement

    # keeps track of the total best cost 
    totalBestCostTbl = [[] for _ in range(2 * numOptimizationSteps)]


    # list of Y positions to start with 
    YTemp = computeArrangements(newProcessingBlockArrangement, Fsizes, qMax)

    # total cost to start with, to be minimized 
    costTotInitial = computeTotalCost(YTemp, nQ)

    costList = [costTotInitial]
    BList = [newProcessingBlockArrangement]

    processingBlockArrangementDisplaying = []

    # iterate over the number of Optimizing steps, given the function as argument 
    for optimizationstep in range(numOptimizationSteps): 

        # deterministic algorithm, returns updated newProcessingBlockArrangement 
        newProcessingBlockArrangement, processingBlockArrangementDisplayingDeterministic = improvePlacement(newProcessingBlockArrangement, nQ, Fsizes, qMax, mMax, False)


        if echo == True: 
            print('echo')

        if visualOutput == True:
            print('visualoutput')

        # Tabu Search algorithm, returns updatet newProcessingBlockArrangement!
        newProcessingBlockArrangement, costProgressList, bestcostProgressList, processingBlockArrangementDisplayingTabuSearch = improvePlacementTabuSearch(newProcessingBlockArrangement, Fsizes, qMax, mMax, nQ, TSiterations, tabuListLength, 3, 0, greedySpread = False, improvementFactor=improvementFactor, storeAllBestprocessingBlockArrangement= True, echo = False)

        processingBlockArrangementDisplaying += processingBlockArrangementDisplayingDeterministic
        processingBlockArrangementDisplaying += processingBlockArrangementDisplayingTabuSearch
        # processingBlockArrangementDisplaying.append(processingBlockArrangementDisplayingTabuSearch)

        # print('total cost 2, iteration ', optimizationstep, 'cost is: ', computeTotalCost(computeArrangements(newProcessingBlockArrangement, Fsizes, qMax), nQ))

        costList.append(computeTotalCost(computeArrangements(newProcessingBlockArrangement, Fsizes, qMax), nQ))
        BList.append(copy.deepcopy(newProcessingBlockArrangement))

        if echo == True: 
            print('')

        if visualOutput == True: 
            print('visualoutput')

        # if we reached the last iteration, one last deterministic algorithm to end on, to get rid of randomness 
        # if optimizationstep == numOptimizationSteps-1: 
        #     newProcessingBlockArrangement, processingBlockArrangementDisplayingDeterministic = improvePlacement(newProcessingBlockArrangement, nQ, Fsizes, qMax, mMax, False)
        #     processingBlockArrangementDisplaying += processingBlockArrangementDisplayingDeterministic
        #     costList.append(computeTotalCost(computeArrangements(newProcessingBlockArrangement, Fsizes, qMax), nQ))
        #     BList.append(copy.deepcopy(newProcessingBlockArrangement))


    # get the B list for which the cost is minimal, argsort sorts from lowest to highest 
    costIndices = np.argsort(costList)
    BList = np.array(BList)
    BList = BList[costIndices]
    bestProcessingBlockArrangement = BList[0]


    # this as well 
    totalBestCostTbl = totalBestCostTbl

    # processingBlockArrangementDisplaying += BList[0]

    # 
    return processingBlockArrangementDisplaying, costList, bestProcessingBlockArrangement
 

# processingBlockArrangementDisplaying ,b,c,numberOfTabuStepsList,costEvolution, newProcessingBlockArrangement = optimizeArrangements(processingBlockArrangement, NQ, FSIZES, QMAX, MMAX, numOptimizationSteps= 10, TSiterations= 10000, tabuListLength= 100, echo = True, visualOutput = False)


# visualize_blocks(processingBlockArrangement, 'Processing block arrangement before optimization, cost: ' + str(computeTotalCost(computeArrangements(processingBlockArrangement, FSIZES, QMAX), NQ)))



# visualize_blocks(newProcessingBlockArrangement, 'After alternating search, cost: ' + str(computeTotalCost(computeArrangements(newProcessingBlockArrangement, FSIZES, QMAX), NQ)))

# bestProcessingBlockArrangement, processingBlockArrangementDisplayingDeterministic = improvePlacement(newProcessingBlockArrangement, NQ, FSIZES, QMAX, MMAX, False)

# visualize_blocks(bestProcessingBlockArrangement, 'After alternating search, fixed, cost: ' + str(computeTotalCost(computeArrangements(bestProcessingBlockArrangement, FSIZES, QMAX), NQ)))



# animate_solving(processingBlockArrangementDisplaying, 'alternating search animation')


# plt.figure()
# plt.plot(costEvolution, label = 'cost')
# plt.title('Evolution of total cost with alternating iterations \n')
# plt.xlabel('Iterations')
# plt.ylabel('Cost')
# plt.legend()
# plt.show()

# how many tabu steps? 
# plt.figure()
# plt.plot(numberOfTabuStepsList, label = '# tabuSteps')
# plt.title('Number of Tabu Steps')
# plt.xlabel('Iterations')
# plt.ylabel('Number')
# plt.legend()
# plt.show()


'''
Show here the circuit
'''

# show_layeredCircuit(10, circuit_of_qubits, layeredcircuit)
# show_circuit_after_optimizing(newProcessingBlockArrangement, 10, circuit_of_qubits)