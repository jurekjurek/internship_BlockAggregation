# from BlockAggregation import *

from Commutation import *
from AlternatingOptimization import *

import time



'''
In this file, we compare the performance (the initial block aggregation cost) between the different initital arrangements 
resulting in the commutation rules to each other. 


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

    # return the maximal relative costimprovement 
    return ((costList[0]) - min(costList)) / costList[0]





def CalculatePossibleImprovement(numberOfIterations, limitOnNumberOfPossibleArrangements = 8, limitConsidered = 20, equalSampling = True): 
    '''
    This function creates the plots of interest in order to compare the performances of the different arrangements with each other 
    numberOfIterations is the times a new randomcircuit is arranged, its possible arrangements are determined and for each of these, the blockaggregation is 
    carried out
    equalSampling indicates if the random circuits we compare to each other should all have an equal number of statistics concerning its possible arrangements 
    If for example, we have 20 circuits C1, ..., C20, and C1 gives us 5 possible alternative circuits due to the commutation behaviour of the gates in 
    this circuit and C2 gives us 4, C3 gives us another 5 and so on, the number will be very unbalanced. 
    We introduce a numpy array called countForEachNo, that counts the number of possible arrangements for each of the circuit. In our example, we might end up with 
    [10,0,3,3,0,4,0,...] where we introduce a limit to the length of this array given by limitOnNumberOfPossibleArrangements. Here, we see that we have no circuit 
    where we have two possible arrangements and 3 for when we have three, another 3 for when we have four and so on. This is not equally sampled. 
    Thus, in order to have an equal amount of statistics for all the different number of possible arrangements, we introduce equalSampling, that executes the code
    until a number (specified by limitOnNumberOfPossibleArrangements) is in the array for *every* possible number of arrangement. The list countForEachNo would then
    look like this at the end of the algorithm: 
            [limitOnNumberOfPossibleArrangements, limitOnNumberOfPossibleArrangements, ..., limitOnNumberOfPossibleArrangements]
    However, this takes very long

    Limitconsidered is a limit for the number of possible arrangements. If there is for example, 100 possible arrangemnts, the chance that we will encounter 
    even one more of this is very low, thus only an insignificant number of statistics is available for these. We typically set limitConsidered = 20 
    '''

    # keep track of time 
    start = time.time()


    relativeCostList = []
    numArrangementsList = []

    # for each possible number of arrangements (up to 20), we keep track of the number of possibilities that have this number of possible arrangemnets
    countForEachNo = np.zeros(limitOnNumberOfPossibleArrangements)

    limitOnCount = 30

    '''
    making sure to have an equal number of possible arrangement for eaach possible lenght of possible arrangements...
    '''

    if equalSampling: 
        while True:

            # debug, see the array being iteratively filled up 
            print(countForEachNo)

            randomCirc = RandomCircuit(20, 40)
            possibleArrangements = randomCirc.FindAllPossibleArrangements()
            
            NoPossibleArrangements = len(possibleArrangements)
            
            if NoPossibleArrangements > limitOnNumberOfPossibleArrangements or NoPossibleArrangements == 5 or NoPossibleArrangements == 7:
                continue
            else: 
                if countForEachNo[NoPossibleArrangements-1] >= limitOnCount:
                    if np.array_equal(countForEachNo, np.array([limitOnCount,limitOnCount,limitOnCount,limitOnCount, 0, limitOnCount, 0, limitOnCount])):
                        print('test')
                        break
                    else: 
                        continue
                else:
                    countForEachNo[NoPossibleArrangements-1] += 1

            tempResult = CompareDifferentArrangements(possibleArrangements)


            numArrangementsList.append(len(possibleArrangements))
            relativeCostList.append( tempResult )

    # if not sampled equally: 
    else:
        for iteration in range(numberOfIterations):
            if iteration % 10: 
                print('iteration: ', iteration)
            
            randomCirc = RandomCircuit(20, 40)
            possibleArrangements = randomCirc.FindAllPossibleArrangements()
            
            NoPossibleArrangements = len(possibleArrangements)
            if NoPossibleArrangements > limitConsidered: 
                continue

            tempResult = CompareDifferentArrangements(possibleArrangements)


            numArrangementsList.append(NoPossibleArrangements)
            relativeCostList.append( tempResult )


    '''
    Here, we actually create the plots 
    we iterate over the number of circuits and for each circuit, we look at the corersponding number of possible arrangements (nArr)
    then we iterate over the rest of the circuits, and check if the circuit shares this nArr. If it does, we take the relativeCostImprovement (determined by 
    the above function) into a sum and in the end, average over the whole thing. 
    What we thus observe is an average over the (BEST POSSIBLE) cost improvement (in percent) for circuits with these particular numbers of arrangements resulting 
    from the commutation behaviour.

    '''

    tabuList = []

    avgList = np.zeros(max(numArrangementsList))
    errorList = np.zeros(max(numArrangementsList))

    indexCount = np.zeros(limitConsidered)

    numberOfCircuits = len(relativeCostList)
    

    for i in range(numberOfCircuits): 
        
        # numArrangements is the length of the arrangement
        numArrangements = numArrangementsList[i]

        # we want to know the frequencies of the occurences of different ArrangementLenghts (only smaller than limit are of interest)
        if numArrangements < limitConsidered: 
            indexCount[numArrangements-1] += 1

        # if we saw this index before or the lenght of the arrangement is one (no commutation induced rearrangement possibilities)
        if numArrangements in tabuList or numArrangements == 1:
            avgList[0] = 0
            # we do not have to average over this, because clearly, if there is no other arrangement possible, the cost improvement will always be zero
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
        errorList[numArrangements - 1] = (np.std(tempCostsForThisArrNo)/np.sqrt(tempCount))

    end = time.time()

    print('TIME:', end - start)

    print(relativeCostList)

    # bar plot for the frequencies
    xValues = np.arange(limitConsidered)
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
    for i in range(0, len(xValues)):
        if avgList[i] != 0 or i < 4: 
            plt.errorbar(xValues[i], avgList[i]*100, yerr = errorList[i]*100, fmt = 'o', color = 'red')
    
    # plt.scatter(numArrangementsList, avgGaugeList, label = 'Without commutation')
    # plt.xlim(0,50)
    plt.xlabel('Numbers of possible arrangements')
    plt.ylabel('MaxCostImprovement / InitialCost [%]')#'(initialcost - bestCost) / initialCost')
    # plt.legend()
    plt.show()




CalculatePossibleImprovement(100)


