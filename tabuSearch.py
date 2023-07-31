import numpy as np
import matplotlib.pyplot as plt

'''
In this file, the so called tabu search is applied to 
'''



def reconstructBlocksFromArrangements(BP, Fsizes, Qmax, Mmax, Nq, Y, zonesTbl, s1Tbl, s2Tbl):
    return None



def improvePlacementTabuSearch(BP, Fsizes, Qmax, Mmax, Nq, TSiterations, TSlen, swapNumMax, processingZoneSwapFraction, greedySpread, soreAllBestBP, echo):

    numF = len(Fsizes)

    numSteps = len(BP)

    idlePools = []

    