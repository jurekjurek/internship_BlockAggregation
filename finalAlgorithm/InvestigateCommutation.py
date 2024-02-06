# from BlockAggregation import *

from Commutation import *
from AlternatingOptimization import *

'''
In this file, the gatecoverage and thus, the cost of the inital arrangements is compared for the different commutations of the inital random circuit
that are allowed as calculated in the file RandomCircuitQiskit.py

Two things will be displayed: 
    The gatecoverage for the different arrangements 
    The cost of the resulting qubit arregations


MISSING: 
    compute errors for the relative performance! 
    find a way to find many circuits of higher length: 
        We want 20 cicuits each of numberArr = 1, 2, 3, 4, 5, 6, 7, 8, 9, ..., 50

'''


def CompareDifferentArrangements(possibleArrangements):
    '''
    given a list of possible circuits, this function determines the cost of the different arrangements *relative* to the initial arrangement
    It returns the best possible relative improvement and the number of arrangements
    '''


    if len(possibleArrangements) == 1: 
        return [0, 1]

    costList = []

    for i in range(len(possibleArrangements)):
        tempCircuit = possibleArrangements[i]
        tempArrangement = blockProcessCircuit(tempCircuit, NQ, FSIZES, QMAX, MMAX)

        costList.append(computeTotalCost(computeArrangements(tempArrangement, FSIZES, MMAX), NQ))

    # costlist[0] corresponds to the initial element that would have been chosen if no commutation had been considered
    return ((costList[0]) - min(costList)) / costList[0] #[((costList[0]) - min(costList)) / costList[0], len(possibleArrangements)]





def CalculatePossibleImprovement(numberOfIterations): 

    relativeCostList = []
    numArrangementsList = []

    limitOnNumberOfPossibleArrangements = 5

    # for each possible number of arrangements (up to 20), we keep track of the number of possibilities that have this number of possible arrangemnets
    countForEachNo = np.zeros(limitOnNumberOfPossibleArrangements)

    '''
    making sure to have an equal number of possible arrangement for eaach possible lenght of possible arrangemnts...
    '''
    # while 0 in countForEachNo:
    #     # if iteration % 10 == 0:
    #     #     print('iteration No. ', iteration)

    #     print(countForEachNo)

    #     randomCirc = RandomCircuit(20, 40)
    #     possibleArrangements = randomCirc.FindAllPossibleArrangements()
        
    #     NoPossibleArrangements = len(possibleArrangements)
        
    #     if NoPossibleArrangements >= limitOnNumberOfPossibleArrangements:
    #         continue
    #     else: 
    #         if countForEachNo[NoPossibleArrangements-1] >= 4:
    #             continue
    #         else:
    #             countForEachNo[NoPossibleArrangements-1] += 1

    #     tempResult = CompareDifferentArrangements(possibleArrangements)


    #     numArrangementsList.append(len(possibleArrangements))
    #     relativeCostList.append( tempResult )


    for iteration in range(numberOfIterations):
        if iteration % 10: 
            print('iteration: ', iteration)
        
        randomCirc = RandomCircuit(20, 40)
        possibleArrangements = randomCirc.FindAllPossibleArrangements()
        
        NoPossibleArrangements = len(possibleArrangements)
        if NoPossibleArrangements > 20: 
            continue

        tempResult = CompareDifferentArrangements(possibleArrangements)


        numArrangementsList.append(NoPossibleArrangements)
        relativeCostList.append( tempResult )


    tabuList = []

    avgList = np.zeros(max(numArrangementsList))
    errorList = np.zeros(max(numArrangementsList))

    indexCount = np.zeros(50)
    
    # for plotting 
    numArrangementsListUnOrdered = []

    for i in range(len(relativeCostList)): 
        
        # numArrangements is the length of the arrangement
        numArrangements = numArrangementsList[i]

        # we want to know the frequencies of the occurences of different ArrangementLenghts (only smaller 50 are of interest)
        if numArrangements < 50: 
            indexCount[numArrangements-1] += 1

        # if we saw this index before or the lenght of the arrangement is one (no commutation induced rearrangement possibilities)
        if numArrangements in tabuList or numArrangements == 1:
            avgList[0] = 0
            if numArrangements == 1: 
                indexCount[0] += 1
            continue

        tabuList.append(numArrangements)

        tempCount = 0
        tempSum = 0
        tempCostsForThisArrNo = []


        # Here, we actually iterate over all possible maxCostImprovements for this particular arrangment number
        for j in range(len(relativeCostList)): 
            if numArrangementsList[j] == numArrangements: 
                tempSum += relativeCostList[j]
                tempCostsForThisArrNo.append(relativeCostList[j])
                tempCount += 1

        avgList[numArrangements - 1] = (np.average(tempCostsForThisArrNo))
        errorList[numArrangements - 1] = (np.std(tempCostsForThisArrNo))

        # avgList.append(tempSum / tempCount)
        # numArrangementsListUnOrdered.append(numArrangements)


    print(relativeCostList)


        # print('Average for possiblearrangements Length ', numArrangements, ' is ', tempSum / tempCount, '. \n Where the number of averages was ', tempCount)


    # bar plot for the frequencies
    xValues = np.arange(50)
    plt.bar(xValues, indexCount)
    plt.xlim(-1, 10.5)
    plt.title('Histogram')
    plt.ylabel('Frequency')
    plt.xlabel('Number of possible arrangements')
    plt.show()

    print(len(numArrangementsList))
    print(len(avgList))

    xValues = np.arange(len(avgList))

    print('errorList: ', errorList)
    print('avgList: ', avgList)

    # print average possible cost improvement for the different iterations
    plt.title('Maximum possible cost improvement in %, with errorbars')
    # plt.scatter(numArrangementsListUnOrdered, avgList, label = 'With commutation')
    for i in range(1, len(xValues)):
        if avgList[i] != 0: 
            plt.errorbar(xValues[i], avgList[i], yerr = errorList[i], fmt = 'o')
    
    # plt.scatter(numArrangementsList, avgGaugeList, label = 'Without commutation')
    # plt.xlim(0,50)
    plt.xlabel('Numbers of possible arrangements')
    plt.ylabel('(initialcost - bestCost) / initialCost')
    plt.legend()
    plt.show()



CalculatePossibleImprovement(300)