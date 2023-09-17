'''
In this file, I will try to apply a genetic algorithm to the problem of uncluttering a graph. 
The metric that guides the minimization procedure is defined in the function computeTotalCost. 

What we essentially start with is a procedure to randomize the idle qubits in each processing block. 
So we iterate over each of the processing blocks, and if natureStatus = 'i', we collect it in an idle pool. 
We scramble the qubits in this idle pool and then reassign them to their positions before. 

We could also do this in the block aggregation procedure. 
'''

from helperFunctions import * 

numberIndividuals = 5
individuals = []
fitnessList = []

for individual in range(numberIndividuals): 

    # create processingBlockArrangement 
    individuals.append(processingBlockArrangement)
    # store the corresponding fitnessvalue in a fitnesslist 

    
