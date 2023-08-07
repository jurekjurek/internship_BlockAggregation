import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.lines import Line
# from matplotlib.patches import Circle
import random
import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import math 

import networkx as nx

 
from randomcircuit import * 
from layeredcircuit import * 

'''
In this file, the mathematica file ... 
will be transcripted into python, extended and commented in order for other people to be able to use it. 

There are a few important files involved in this project. 
The first one is randomcircuit.py - it creates a random circuit and plots it using qiskit. 

The second one is layeredcircuit.py - it creates a layered circuit given a raw circuit as input 

The third one is blockprocessing.py - it applies the block aggregation algorithm to the layered circuit. 

What is also of interest is: 
    1. The commutation rule: Not only do two gates commute if they just do not share two qubits. It is possible to have more general commutation rules. Implement this. 
    2. 

'''


circuit_of_qubits = random_circuit(10, 20)

# show_circuit(10,circuit_of_qubits)

layeredcircuit = LayerCircuit(10, circuit_of_qubits)
# print(layeredcircuit)
# show_layeredCircuit(10, circuit_of_qubits, layeredcircuit)


'''
Now that we have the layered circle going, we can focus on the block aggregation. 
This will be done ... 

Structure: 
Aggregation step - Postprocessing step - Qubit Placement - ...
repeat until termination condition is satisfied 

'''

def EvaluateGateCoverage(S, G, Nq, Qmax, Mmax):
    '''
    evaluates gate coverage given: 
        1. A set of qubit sets S
        2. A gate Coverage set G
        3. The total number of qubits 
        4. The maximal number of qubits in a processing zone Qmax  
        5. The maximal number of processing zones Mmax

    returns two ints gateCoverage and qubitNonCoverage, indicating 
        1. how many gates are covered with this constellation and 
        2. the number of qubits that are in sets that are bigger than the maximum number of qubits in a processing zone. These qubits cannot be covered anymore

    The gateCoverage is to be maximized in the course of this algorithm 

    '''

    # initialize variables of interest to zero 
    gateCoverage = 0

    # Number of qubits that cannot be covered, because the corresponding sets are larger than the maximal number of Qubits in a processing zone Q
    qubitNonCoverage = 0

    # define running variable 
    processingzone_no = 1

    # iterate over elements in qubit sets 
    for n in range(len(S)):

        # if one specific set of qubits has more elements than can be stored in the processing zone, the number of qubits that cannot be covered is increased 
        if len(S[n]) > Qmax: 
            qubitNonCoverage += len(S[n])

        # if the number of qubits in a set is still in the range of possible qubits in a processing zone, and we populate one of the possible processing zones whose number is limited by Mmax:
        if len(S[n]) <= Qmax and processingzone_no <= Mmax: 

            # we increase the gatecoverage 
            gateCoverage += len(G[n])

            # and we jump to the next processing zone 
            processingzone_no += 1  

    return gateCoverage, qubitNonCoverage



# def InitBlockAggregation():
#     S = []
#     G = []
#     c = []
#     S_b = []
#     G_b = []
#     return S, G, c, S_b, G_b


'''

G_n, so one specific element of the G list indicates what gates are covered by the Qubit Set S_n  
Mmax is the number of processing zones in one processing block 

'''

def AggregateBlocksStep(layeredCirc, Nq, Qmax, Mmax):
    '''
    The goal is to find the set of S and G that produce the best GateCoverage!!
    '''

    # S is a list of lists! G is a list of lists! 
    # At the beginning, S is of length Nq, but in the course of the algorithm, the qubits as well as the gates are merged together and S gets shorter with increasingly bigger elements.


    # before starting the iteration over layers and gates, initialize the S and G lists
    # The s list, the list containing the qubits, will be initialized as follows: S = [[1],[2],...], so the first qubit set contains only the first qubit, the second set only the second qubit and so on
    S = [[n] for n in range(Nq)]


    # same for the gate coverage sets
    G = [[] for _ in range(Nq)]
    G_test = [[None] for _ in range(Nq)]
    G_np = np.array(G_test)
    # print(np.shape(G_np))
    # G_np = np.full(Nq, np.array([None]), dtype=object)

    # also the pointer variables will be initialized, in the beginning cn = n, because every qubit has its own set S_n, later the sets will get merged and more qubits will have the same cn
    ctbl = [n for n in range(Nq)]


    # shall be overwritten quickly, 
    S_best = []
    G_best = []

    # initialize gate coverage counter, the variable to be maximized
    bestGateCoverage = 0

    # for debugging
    gatecoverage_list = []

    # iterate over layers 
    for layer_no in range(len(layeredCirc)):
        
        # iterate over gates in layers 
        for gate_no in range(len(layeredCirc[layer_no])):
            gate = layeredCirc[layer_no][gate_no]
            
            # define qubit one and two, that are part of the gate gate_no in layer layer_no 
            QB_n = gate[1][0]
            QB_m = gate[1][1]

            # print("Qubits one and two: ", QB_n, QB_m)
            # print('belonging to gate ', gate)

            # now we define, for this specific for loop, the two pointers cm and cn. We get them from the pointer list ctbl
            # Remember: cm and cn are just two numbers. 
            # To what qubit set do the two qubits belong? 
            cn = ctbl[QB_n]
            cm = ctbl[QB_m]

            # print('Corresponding pointers to qubit sets: ', cn, cm)
            
            # append gate (which is not just a number) to gate coverage set of qubit set corresponding to cn
            if G[cn] != []:
                G[cn].append(gate[0])
            if G[cn] == []:
                G[cn] = [gate[0]]
            
            print(G_np[cn], G_np, gate[0])
            G_np[cn] = gate[0]

            print(G_np[cn], G_np, gate[0], type(G_np), np.shape(G_np))

            # if cn and cm are equal, meaning they are part of the same qubit set, continue
            if cn == cm: 
                continue        # we don't have to merge the Qubit sets 

            # Merge Qubit sets
            # We always merge the smaller to the larger set. So if the set belonging to cm is larger than the set belonging to cn, swap them 
            if len(S[cn]) < len(S[cm]):
                temp = cm
                cm = cn 
                cn = temp

            # We merge the qubit sets together
            S[cn] = S[cn] + S[cm]

            # And we merge the gate coverage sets together
            # Remember: Gate n connects qubits n and m, so we dont have to append the gate to G[cm] as well, if we did, we would have it twice 
            G[cn] = G[cn] + G[cm]

            # a = np.array(G_np[cn])
            # b = np.array(G_np[cm])


            # print(a, b)
            if G_np[cn] != None and G_np[cm] != None: 
                print('Want to concatenate:', G_np[cn], G_np[cm])
                np.concatenate((G_np[cn], G_np[cm])) 
        
            # G_np[cn] = np.append(G_np[cn], temp_np)



            # All the pointers that belonged to the qubits in set S[cm] will now be pointing to set S[cn]
            for i in range(len(S[cm])):

                # qubits are just numbers in the code, so S[cm][i] returns exactly the n-th qubit of all qubits. 
                ctbl[S[cm][i]] = cn     # all elements in S[cm] which represent qubits stored as numbers are assigned an element in the ctbl list corresponding to cn

            # The qubit set S[cm] is emptied 
            S[cm] = []

            # The gate coverage set corresponding to Set cm is emptied, because it was merged above
            G[cm] = []
            G_np[cm] = [None]

            # G_np[cm] = np.empty(1)

            # print('the list looks like this:', S)
            # print('the gatelist looks like this:', G)
            # print('the pointerlist looks like: ', ctbl)

            # Remember: S is sorted list and G is a sorted list
            # They are sorted by size; biggest qubits sets as first elements, biggest gate coverage sets as first elements

            # first, let's take care of the set cn that we appended stuff to:
            # if cn is not the first element in the list already (if we append something to the biggest element, it stays the biggest element), we dont have to do anything 
            if cn > 0:

                # we want to move S[cn] to the appropriate position in S. Compare to the element that is one element after it in the list. If it is bigger, move S[cn] up one element
                while (len(S[cn]) > len(S[cn-1]) and cn != 0) or G[cn-1] == None:
                    
                    # in the pointer list ctbl, assign cn to all elements that are assigned cn - 1

                    # What's happening here is essentially swapping all the elements in the lists ctbl, G and S accordingly. 

                    # remember: We effectively move S[] up in the set of qubits S, so upon moving up one step, we effectively replace S[cn] and S[cn-1] as well as the pointers that point to them;
                    # the pointers of the qubits that are stored in set cn will become cn-1 and vice versa 
                    for k in range(len(S[cn])):
                        ctbl[S[cn][k]] = cn - 1

                    for k in range(len(S[cn-1])):
                        ctbl[S[cn-1][k]] = cn


                    # swap the two elements S[cn] and S[cn-1], effectively moving S[cn] up one element in the list. 
                    templist = S[cn]
                    S[cn] = S[cn-1]
                    S[cn-1] = templist

                    # swap the two elements G[cn] and G[cn-1]
                    templist = G[cn]
                    G[cn] = G[cn-1]
                    G[cn-1] = templist 

                    cn -= 1

            # now, for the second list element corresponding to the pointer cm 
            # if cm is not the last element in the list already (if we clear the last element of the list, )
            # We cannot just append [] to the end of S and G, since we have to move the stuff inside the ctbl list as well

            if cm < Nq-1:

                # if cm < len(S):
                #     break 

                while len(S[cm+1]) > 0:
                    for k in range(len(S[cm+1])):
                        ctbl[S[cm+1][k]] = cm

                    S[cm] = S[cm+1]
                    S[cm+1] = []

                    G[cm] = G[cm+1]
                    G[cm+1] = []        

                    cm += 1



                    if cm >= len(S)-1:
                        break
                



            '''
            At this point, the sets have been merged and sorted. Now, to evaluate how well the gates are covered by these particular sets. 
            '''        

                
            # Now that the qubit set as well as the gate coverage set are updatet, check the gate coverage
            # So: How many gates are covered by the Qubit sets S = [S_1, S_2, ...] ?

            gateCoverage1, qubitNonCoverage = EvaluateGateCoverage(S, G, Nq, Qmax, Mmax)

            # termination condition: 
            # if the remaining qubits - those that can be covered by the constellation (excluding these that cannot be covered because they are more than Q) - are less than the qubits that can be stored in the processing zones 
            # in total, so Mmax (no of processing zones) times Qmax (no of qubits in processing zones)
            if Nq - qubitNonCoverage < Mmax * Qmax: 

                print('Termination condition reached!')
                # function returns S_best and G_best, because we're running out of space 

                print(np.shape(G_best))
                return S_best, G_best, gatecoverage_list
            
            zoneCtr = 1
            gateCoverage = 0



            # essentially the same as is done in EvaulateGateCoverage???


            # evaluate the gate coverage for this specific constellation of sets 
            for qubitset_no in range(len(G)):
                if len(S[qubitset_no]) < Qmax and zoneCtr <= Mmax:
                    gateCoverage += len(G[qubitset_no])
                    zoneCtr += 1


            gatecoverage_list.append(gateCoverage1)

            # if the gatecoverage for this particular constellation of sets is better than for the last constellation of sets
            if gateCoverage1 > bestGateCoverage: 
                bestGateCoverage = gateCoverage1
                

                # also, this particular constellation of Qubit sets and of Gate sets are updatet as the best ones so far 
                # S_best = S.copy()
                # G_best = G.copy()

                S_best = np.copy(S)
                G_best = np.copy(G)


    return S_best, G_best, gatecoverage_list        
            


S_best, G_best, GC_list = AggregateBlocksStep(layeredcircuit, 10, 4, 1)

print(np.shape(G_best))
print(G_best)


# Plot the blockaggregation procedure  

# plt.figure()
# plt.title('Developement of the gatecoverage during blockaggregation \n')
# plt.plot(GC_list)
# plt.ylabel('Gatecoverage')
# plt.xlabel('Iterations')
# plt.show()


def AggregateBlocksStepPostProcess(S, G, Nq, Qmax, Mmax):
    '''
    Given:
        S - A set of qubits

    After the block aggregation step, this function does a couple of things: 
        1. It selects the sets to be used as processing zone sets 
        2. It pads these sets with additional idle qubits 
        3. It fills all the remaining qubits into a global Idle pool
        4. It builds a new structure of pointer variables for further processing 

    Each pointer variable to qubit q is now a quadruple: {s, m, k, s'}, where: 
        s = {'p', 'i'}:  indicates if q is stored in processing zone or idle pool 
        m = {0, ...}  processing zone number 
        k = {1, ...} position within processing zone or idle pool 
        s'= {'a', 'i'} active or idle (within processing zone, the qubits in idle pool are always idle / inactive.)

    '''

    # set of processing zone sets 
    SP = []

    # set of covered gates corresponding to processing zone sets 
    GP = []

    c = [[] for _ in range(Nq)]

    # Idle pool qubits
    Iset = []

    # essentially a processing zone counter 
    m = 0

    # iterate over the aggregated sets (processing blocks so far)
    for n in range(len(S)):

        # if this particular set of qubits fits into the processing zone, append to processing zone sets and corresponding gate coverage set
        if len(S[n]) <= Qmax and m <= Mmax - 1: 
            SP.append(S[n])
            GP.append(G[n])

            # first position is zeroth position
            k = 0

            # assign pointers to the qubits in this set 
            for qi in range(len(S[n])):
                q =  S[n][qi]
                c[q] = ['p', m, k, 'a']
                k += 1 

            # now that this processing zone has been filled, focus on next one 
            m += 1   

           
        # if the qubits do not fit into the processing zone, we add them to the idle pool!    
        else:
            Iset = Iset + S[n]  

    # now, all the processing zone sets with good sizes are padded with qubits from the idle pool 

    # iterate over processing zones 
    for m in range(Mmax):

        # idle subset of processing zone m 
        SPi = []

        # if there is only one qubit in the m-th processing zone
        if len(SP[m]) == 1:

            # take this qubit 
            q = SP[m][0]

            # and empty this list 
            SP[m] = []

            # append this qubit to the idle subset of the processing zone m 
            SPi = [q]

            # this qubit is now idle, but it is still in a processing zone, not a storage zone  
            c[q] = ['p', m, 1, 'i']
        
        # a qubit that is appended to a certain processing zone will have this position: 
        k = len(SP[m]) + len(SPi)

        # while all qubits (active and idle) in the processing zone are less than the maximum possible number of qubits in the processing zone, 
        # we pad the processing zone with more idle qubits from the idle pool 
        while len(SP[m])+ len(SPi) < Qmax:

            # take the first qubit in the idle pool
            q = Iset[0]

            # append the qubit from the idle pool to the idle subset of the processing zone 
            SPi.append(q)

            # and adjust its pointer accordingly, it's idle, but now in a processing zone 
            c[q] = ['p', m, k, 'i']

            # erase this qubit from the idle pool - it was moved to the processing zone 
            Iset = Iset[1:]
            k += 1 
        
        # update the qubits in processing zone m 
        SP[m] = SP[m] + SPi

    # end of for loop 

    # now, as a last step, assign the poiniter variables for all qubits remaining in the global idle pool 
    for qi in range(len(Iset)):
        q = Iset[qi]

        # qubits are idle in idle pool, no processing zones in idle pool - number always 1
        c[q] = ['i', 1, qi, 'i']


    return SP, GP, Iset, c



# test 
SP, GP, Iset, c = AggregateBlocksStepPostProcess(S_best, G_best, 10, 4, 2)

print('sbest:', S_best) 
print('gbest:', G_best)
print('SP:', SP)
print('GP:', GP)



'''
Now, we have padded the processing zones with idle qubits, so the processing zones are now filled with active and idle qubits. 
We are done with the processing zones. 

Now, as one last step, we have to take the qubits from the idle pool and place them into storage zones in the processing blocks. 
'''


def PlaceIdlePoolQB(Fsizes, Iset, c):
    '''
    Given: 
        Fsizes, a list of sizes of storage zones. E.g. for two storages zones with size 10 each: Fsizes = [10,10]
    Returns: 
        Fset, a set of storage zones filled with qubits 

    this function places qubits from a global idle pool into idle storage zones with max capacities specified by F sizes 
    The qubits, in this version, are placed starting from the middle, outwards. 
    '''

    # number of storage zones: 
    numF = len(Fsizes)

    # first storage zone to be filled up, remember: we're starting in the middle, keeping in mind the indexing by python
    f = math.floor(numF / 2) - 1

    # initialize empty storage zones, list of empty lists
    Fset = [[] for _ in range(numF)]

    # idle pool, create a copy that will be continuosly decreased 
    Isetnew = Iset
    
    # pointer table 
    cnew = c 

    # Now, to fill up these idle zones. We start in the starting zone, moving left and right, filling up the zones 
    # we go through the storage zones starting with a right zone, corresponding to fp, then a left zone, corresponding to fm 
    fm = f
    fp = f+1 
    ctr = 1 

    # while there's still qubits left in the idle pool 
    while len(Isetnew) > 0: 

        '''
        Right zone
        '''
        # if we are still within the allowed number of storage zones but the number of qubits in this storage zone is too high, move to the left 
        if fp <= numF and len(Fset[fp]) >= Fsizes[fp]:
            fp += 1

        # if we are within the allowed number of storage zones and the fp-th storage zone still needs to be filled 
        if fp < numF and len(Fset[fp]) < Fsizes[fp]:

                # take the first qubit in the idle pool 
                q = Isetnew[0]

                # append this qubit to the storage zone 
                Fset[fp].append(q)

                # and adjust their pointer variables accordingly, where fp is the number of the storage zone
                cnew[q] = ['i', fp, len(Fset[fp])-1, 'i']

                # eliminate qubit q from idle pool 
                Isetnew = [x for x in Isetnew if x != q]

        '''
        Left zone 
        '''
        # if within the allowed number of storage zones and the fm-th storage zone is too full 
        if fm >= 0 and len(Fset[fm]) >= Fsizes[fm]:
            fm -= 1
        
        # if the fm-th storage zone still has to be filled 
        if fm >= 0 and len(Fset[fm]) < Fsizes[fm]:

            # take the first qubit in the idle pool 
            q = Isetnew[0]

            # append this qubit to the storage zone 
            Fset[fm].append(q)

            # and adjust their pointer variables accordingly 
            cnew[q] = ['i', fm, len(Fset[fm])-1, 'i']

            # eliminate qubit q from idle pool 
            Isetnew = [x for x in Isetnew if x != q]


        # if all storage zones are filled up and there's qubits left in the idle pool, error 
        if fp == numF and len(Fset[fp]) >= Fsizes[fp] and fm == 1 and len(Fset[fm]) >= Fsizes[fm] and len(Isetnew) > 0:
            print('ERROR: No more storage zones left, but not all qubits placed.')
            return Fset, cnew

    return Fset, cnew          


# test of storage zone algorithm, funktioniert. 
Fsizes = [3, 3]



'''
Now, all subalgorithms have been taken care of.
We can implement the main algorithm 
'''


def blockProcessCircuit(rawCircuit, Nq, Fsizes, Qmax, Mmax):
    '''
    This is the Main function executing the Block aggregation algorithm step by step. 

    This function step by step removes gates from the given circuit rawCircuit, based on  

    Accepts: 
    rawCircuit: The raw Circuit, 
    Nq:         the number of Qubits in the circuit, 
    Fsizes:     The sizes of the processing zones 
    Qmax:       The maximal number of Qubits that can be stored within a processing zone 
    Mmax:       The number of processing zones within a processing block 

    Returns: 
    B:          List of aggregated processing blocks

    '''

    # Raw Circuit to be manipulated 
    cRaw = rawCircuit

    # list of aggregated blocks 
    B = []

    i = 0

    # while stuff still left in circuit 
    while cRaw != []:
        # Make layeredcircuit
        C                   = LayerCircuit(Nq, cRaw)


        # Get best set of qubits and gates from algorithm 
        S_best, G_best, gc_list_test      = AggregateBlocksStep(C, Nq, Qmax, Mmax)

        # Get set of qubits and gates, for the different processing zones. And the 'remaining' idle pool Iset 
        SP, GP, Iset, c     = AggregateBlocksStepPostProcess(S_best, G_best, Nq, Qmax, Mmax)

        # Finally, fill storage zones with qubits in 'remaining' idle pool 
        FP, cnew            = PlaceIdlePoolQB(Fsizes, Iset, c)

        # iterate over the different sets of gates in GP
        for gpi in range(len(GP)):

            cRaw = [cRaw[i] for i in range(len(cRaw)) if i not in GP[gpi]]


            # iterate over the gates in the gates sets corresponding to qubit sets in the processing zones 
            # for gi in range(len(GP[gpi])):

                # print(cRaw[gi][0], GP[gpi][gi])

                # Remove the covered gate from the circuit
                # for k in range(len(cRaw)):
                    # if cRaw[k][0] == GP[gpi][gi]:
                # cRaw.pop(GP[gpi][gi])    
                # break
                # cRaw = [x for x in cRaw if x != GP[gpi][gi]]
        
        # append this set of S, G, F and c to the collection of processing blocks 
        B.append([SP, GP, FP, cnew])

        print('cRaw looks like:',cRaw)
        print('where GP is:', GP)

    return B


# test of the whole algorithm 
# seems to work 

B = blockProcessCircuit(circuit_of_qubits, 10, Fsizes, 4, 1)



'''
Displaying 
'''

def visualize_blocks(B):
    '''
    Given a list B, this function plots the qubits in the corresponding processing blocks. Same qubits are connected to each other between neighbouring layers. 

    Accepts: 
        B:          List of interest in optimization procedure 
    Returns: 
        Nothing 

    '''

    # extract c from B
    c_total = []
    for i in range(len(B)):
        c_total.append(B[i][3])

    # Graph 
    G = nx.Graph() 

    

    # add nodes for all the qubits in the different layers 
    # every qubit gets assigned a zone keyword indicating in what zone it is and a label keyword indicating what number qubit it is. Also a layer number indicating what layer it is in. 

    # iterate over blocks 
    for layer_no in range(len(c_total)):

        # iterate over qubits in block 
        for qb_no in range(len(c_total[layer_no])):

            # if in storage zone, add with corresponding label and zone keyword 
            if c_total[layer_no][qb_no][0] == 'i':
                G.add_node((layer_no, qb_no), layer=layer_no, zone='storage', label=str(qb_no))

            # if in storage zone, add with corresponding label and zone keyword, remember: qbs can still be idle in processing zone, so we have to differentiate 
            elif c_total[layer_no][qb_no][0] == 'p': 

                if c_total[layer_no][qb_no][3] == 'i':
                    G.add_node((layer_no, qb_no), layer=layer_no, zone='processing_idle', label=str(qb_no))

                elif c_total[layer_no][qb_no][3] == 'a':
                    G.add_node((layer_no, qb_no), layer=layer_no, zone='processing_active', label=str(qb_no))

            print(G.nodes())

    # assign positions to all the qubits 
    pos = {}
    for node in G.nodes():

        # node is a tuple, node = (layer_number, node_number)
        layer_idx, node_idx = node
        
        # x position is just the layer number 
        x = layer_idx

        # depending if in storage, or processing zone, assign y coordinates 
        # storage zone 
        if c_total[layer_idx][node_idx][0] == 'i':
            y = c_total[layer_idx][node_idx][1]*-7 - c_total[layer_idx][node_idx][2]

        # processing zone 
        elif c_total[layer_idx][node_idx][0] == 'p':
            y = -3 - c_total[layer_idx][node_idx][2]

        # pos is a dictionary, pos((processingblock_number, qubit_number) = (x, y)). 
        # pos stores this for all the qubits in all the blocks 

        pos[node] = (x, y)


    # add edges 
    # We always add an edge between a qubit and the one in the layer next to it on the right. So, for the rightmost layer, we do not have to add an edge.
    for layer_no in range(len(c_total)-1):
        for qb_no in range(len(c_total[layer_no])):

            # current node is tuple
            current_node = (layer_no, qb_no)

            # want to find the node in the layer next to it on the right that has the same label (corresponds to the same qubit)
            for qb_no_ in range(len(c_total[layer_no+1])):

                # if we found the qubit with the same label 
                if G.nodes[current_node]['label'] == G.nodes[(layer_no+1, qb_no_)]['label']:
                    next_node = (layer_no + 1, qb_no_) 

                    # add an edge connecting these two nodes to the graph 
                    G.add_edge(current_node, next_node)

    # clarifying that the label keyword is actually the label that we want to use 
    node_labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, node_size=400, node_color=['red' if G.nodes[node]['zone'] == 'storage' else 'green' if G.nodes[node]['zone'] == 'processing_active' else 'blue' for node in G.nodes()], labels=node_labels, with_labels=True)
    plt.title('Qubits in processing blocks \n')
    plt.show()       


# visualize_blocks(B)



