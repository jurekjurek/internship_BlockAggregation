'''
In this file, we create some plots tracking the performance of the different algorihtms 

We iterate numberIteration times, in each step we create a new processingBlockArrangement

'''
from AlternatingOptimization import *
from Commutation import *


# start by defining global variables, properties of the circuit. 
# Where FSIZES has to match NQ and GATES
NQ = 20
GATES = 40
MMAX = 2
QMAX = 4
FSIZES = [4,4,4]

# showPlots indicates if plots should be displayed or not 
showPlots = False
showAnimations = False


numberIterations = 1

# define three costLists for deterministic, Tabu Search and Alternating optimization

costListDet = np.zeros(numberIterations)
costListTabu = np.zeros(numberIterations)
costListAlt = np.zeros(numberIterations)


for iteration in range(numberIterations):

    '''
    BLOCKAGGREGATION STARTING FROM RANDOM CIRCUIT
    '''

    circuitOfQubits = RandomCircuit(NQ, GATES).gatesList

    processingBlockArrangement = blockProcessCircuit(circuitOfQubits, NQ, FSIZES, QMAX, MMAX)


    # cost of the initial arrangement
    initialCost = computeTotalCost(computeArrangements(processingBlockArrangement, FSIZES, MMAX), NQ)


    '''
    DETERMINISTIC OPTIMIZATION
    '''

    processingBlockArrangementAfterDeterministicOptimization, processingBlockArrangementDisplaying = improvePlacement(processingBlockArrangement, NQ, FSIZES, QMAX, MMAX, False)


    costListDet[iteration] = (computeTotalCost(computeArrangements(processingBlockArrangementAfterDeterministicOptimization, FSIZES, MMAX), NQ))





    '''
    TABU SEARCH
    '''


    processingBlockArrangementAfterTabuSearch, costProgressList, bestcostProgressList, processingBlockArrangementDisplaying = improvePlacementTabuSearch(processingBlockArrangement, FSIZES, QMAX, MMAX, NQ, TSiterations=600, tabuListLength=30, swapNumMax=3, processingZoneSwapFraction=0, greedySpread=False)

    costListTabu[iteration] = (computeTotalCost(computeArrangements(processingBlockArrangementAfterTabuSearch, FSIZES, MMAX), NQ))

    '''
    ALTERNATING OPTIMIZATION
    '''
    processingBlockArrangementDisplaying, costEvolution, processingBlockArrangementAfterAlternatingSearch = optimizeArrangements(processingBlockArrangement, NQ, FSIZES, QMAX, MMAX, numOptimizationSteps= 15, TSiterations= 10000, tabuListLength= 100, echo = True, visualOutput = False)

    costListAlt[iteration] = (computeTotalCost(computeArrangements(processingBlockArrangementAfterAlternatingSearch, FSIZES, MMAX), NQ))





detList = (costListDet/initialCost)
tabuList = (costListTabu/initialCost)
altList = costListAlt/initialCost


print('deterministic average: ', np.mean(detList))
print('tabu average: ', np.mean(tabuList))
print('alternating average: ', np.mean(altList))