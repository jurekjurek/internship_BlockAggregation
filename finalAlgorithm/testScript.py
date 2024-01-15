from AlternatingOptimization import *



'''
This file contains a testrun over all the functions that are defined within this project. 
'''


# start by defining global variables, properties of the circuit. 
# Where FSIZES has to match NQ and GATES
NQ = 20
GATES = 40
MMAX = 2
QMAX = 4
FSIZES = [4,4,4]

# showPlots indicates if plots should be displayed or not 
showPlots = True  
showAnimations = False


'''
BLOCKAGGREGATION STARTING FROM RANDOM CIRCUIT
'''

asdf, circuitOfQubits, tempCircList = CreateRandomCircuit(NQ, GATES, 2, display= False)

processingBlockArrangement = blockProcessCircuit(circuitOfQubits, NQ, FSIZES, QMAX, MMAX)


if showPlots: 
    temporaryCost = computeTotalCost(computeArrangements(processingBlockArrangement, FSIZES, MMAX), NQ)
    visualize_blocks(processingBlockArrangement, 'Qubits arranged in processing blocks, cost: ' + str(temporaryCost))



'''
DETERMINISTIC OPTIMIZATION
'''

processingBlockArrangementAfterDeterministicOptimization, processingBlockArrangementDisplaying = improvePlacement(processingBlockArrangement, NQ, FSIZES, QMAX, MMAX, True)

if showPlots: 
    temporaryCost = computeTotalCost(computeArrangements(processingBlockArrangementAfterDeterministicOptimization, FSIZES, MMAX), NQ)
    visualize_blocks(processingBlockArrangementAfterDeterministicOptimization, 'Processing block arrangement after deterministic optimization, cost: ' + str(temporaryCost))



if showAnimations: 
    animate_solving(processingBlockArrangementDisplaying, 'Animation of deterministic optimization')



'''
TABU SEARCH
'''


processingBlockArrangementAfterTabuSearch, costProgressList, bestcostProgressList, processingBlockArrangementDisplaying = improvePlacementTabuSearch(processingBlockArrangement, FSIZES, QMAX, MMAX, NQ, TSiterations=600, tabuListLength=30, swapNumMax=3, processingZoneSwapFraction=0, greedySpread=False, improvementFactor=0)

if showPlots: 
    temporaryCost = computeTotalCost(computeArrangements(processingBlockArrangementAfterTabuSearch, FSIZES, MMAX), NQ)
    visualize_blocks(processingBlockArrangementAfterTabuSearch, 'Processing block arrangement after tabu search, cost: ' + str(temporaryCost))

if showAnimations: 
    animate_solving(processingBlockArrangementDisplaying, 'Animation of optimization with tabu search')

processingBlockArrangementAfterTabuSearch, costProgressList, bestcostProgressList, processingBlockArrangementDisplaying = improvePlacementTabuSearch(processingBlockArrangement, FSIZES, QMAX, MMAX, NQ, TSiterations=600, tabuListLength=30, swapNumMax=3, processingZoneSwapFraction=0, greedySpread=True, improvementFactor=0)

if showPlots: 
    temporaryCost = computeTotalCost(computeArrangements(processingBlockArrangementAfterTabuSearch, FSIZES, MMAX), NQ)
    visualize_blocks(processingBlockArrangementAfterTabuSearch, 'Processing block arrangement after tabu search, cost: ' + str(temporaryCost))

processingBlockArrangementAfterTabuSearch, costProgressList, bestcostProgressList, processingBlockArrangementDisplaying = improvePlacementTabuSearch(processingBlockArrangement, FSIZES, QMAX, MMAX, NQ, TSiterations=600, tabuListLength=30, swapNumMax=3, processingZoneSwapFraction=0, greedySpread=False, improvementFactor=0)

if showPlots: 
    temporaryCost = computeTotalCost(computeArrangements(processingBlockArrangementAfterTabuSearch, FSIZES, MMAX), NQ)
    visualize_blocks(processingBlockArrangementAfterTabuSearch, 'Processing block arrangement after tabu search, cost: ' + str(temporaryCost))

# investigate tabu search further -> run it multiple times and look at the average cost improvement 


'''
ALTERNATING OPTIMIZATION
'''
exit()

processingBlockArrangementDisplaying, costEvolution, processingBlockArrangementAfterAlternatingSearch = optimizeArrangements(processingBlockArrangement, NQ, FSIZES, QMAX, MMAX, numOptimizationSteps= 15, TSiterations= 10000, tabuListLength= 100, echo = True, visualOutput = False)

if showPlots: 
    temporaryCost = computeTotalCost(computeArrangements(processingBlockArrangementAfterAlternatingSearch, FSIZES, MMAX), NQ)
    visualize_blocks(processingBlockArrangementAfterAlternatingSearch, 'Processing block arrangement after alternating search, cost: ' + str(temporaryCost))

    plt.figure()
    plt.plot(costEvolution, label = 'cost')
    plt.title('Evolution of total cost with alternating iterations \n')
    plt.xlabel('Iterations')
    plt.ylabel('Cost')
    plt.legend()
    plt.show()



if showAnimations: 
    animate_solving(processingBlockArrangementDisplaying, 'Animation of optimization with tabu search')





