import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import random
import matplotlib.animation as animation

def random_circuit(Nq, Dg):
    '''
    Nq = number of qubits
    Dg = number of gates

    This function returns a np.array of gatenumbers with corresponding qubit numbers. 
    [[GateNo, [QubitNo1, QubitNo2]], [...], ..., [...]]

    It creates a random circuit. Based on the format in which we will get the raw circuit, we can adjust the function to return the raw circuit in the desired form. 

    '''
    circ = np.zeros((Dg, 2), dtype=object)
    
    for i in range(Dg):

        # choose two integers corresponding to two qubits in the range 1, Number of Qubits without replacement. So the same number does not occur twice. 
        QB_list = random.sample(range(Nq), 2)

        QB_array = np.array(QB_list)

        circ[i] = np.array([i, np.sort(QB_array)])
    
    return circ



def show_circuit(Nq, circ):
    '''
    This function uses qiskit to display a circuit with Nq qubits. The gates are displayed as dictated by the circ list created in the function random_circuit. 
    '''

    q_a = QuantumRegister(Nq, name='q')
    circuit = QuantumCircuit(q_a)
    
    for g in range(len(circ)):

        circuit.cz(q_a[circ[g][1][0]], q_a[circ[g][1][1]], label=str(g+1))
    circuit.draw(output='mpl', fold = 50)#, justify='none')
    plt.show()
    print(circuit)




def reconstructBlocksFromArrangements(processingBlockArrangementOld, storageZoneSizes, qMax, mMax, nQ, yPositionList, zoneNumberList, zoneStatusList, natureStatusList):
    '''
    This function iteratively creates a new B list, given an old B list and a corresponding list with Y positions. 

    It rearranges the qubits in the B list according to the list of y positions Y. 

    For each element in the Y list, it creates a processing block in the new B list. 


    For efficiency reasons, the tabu search algorithm below does not operate on the processingBlockArrangement data structure itself.  
    It merely updates the list of Y positions, the zone tables and the s1 Tables. (s2 never changes, an active qubit stays active, an idle qubit stays idle)
    For this reason, this function, after the execution of the Tabu Search, rebuilds the processingBlockArrangement list, most importantly the c list
    
    Accepts: 

        processingBlockArrangementold:          input processingBlockArrangement structure
        Fsizes:         table of idle storage zone capacities
        qMax:           Processing zone capacity
        mMax:           Number of processing zones
        nQ:             Number of qubits
        Y:              arrangements, output of tabu search
        zoneNumberList:       table of zone indices for each step, output of tabu search
        zoneStatusList:          table of QB status "i" or "p", output of tabu search
        s2Tabl:         table of QB status "a" or "i", not affected by tabu search

    Returns:

        processingBlockArrangementnew:          reconstructed processingBlockArrangement structure

    '''

    # create new B list to be filled iteratively
    processingBlockArrangement = []

    # create a table of qubits? 
    qubitList = np.arange(nQ)
    
    # iterate over all the blocks in the Y list 
    for processingBlock in range(len(yPositionList)):

        # get the list of the qubits in this step, [::-1] reverses the list 
        listOfAllQubitsSort = qubitList[np.argsort(yPositionList[processingBlock])][::-1]

        # get the old GP, this will stay the same. Remember: The gates that are covered will not change, since the qubits will not move in- or out of the processing zones. Only their arrangements within the processing 
        # zones will be adapted. 
        coveredGates = processingBlockArrangementOld[processingBlock][1]

        processingZoneQubits = [[] for _ in range((mMax))]

        # create a new F array to be filled 
        storageZoneQubits = [[] for _ in range(len(storageZoneSizes))]

        # create a new c array to be filled 
        pointerQuadruple = [[] for _ in range(nQ)]

        # for processing and idle qubits, create empty arrays to be filled with positions?
        # processing zone qubits 
        positionInProcessingZoneList = np.ones(mMax, dtype=int)

        # idle zone qubits 
        positionInStorageZoneList = np.ones(len(storageZoneSizes), dtype=int)
        
        # iterate over all qubits in the processing block 
        for qubitNo in range(nQ):

            # get qubit corresponding to number qi 
            qubit = listOfAllQubitsSort[qubitNo]

            # WHAT EXACTLY DO zoneStatusList AND natureStatusList DO? 
            # s1 corresponds to s, s2 corresponds to s', meaning: 
            # s1 indicates if the qubit is stored in idle or processing zone 
            zoneStatus = zoneStatusList[processingBlock][qubit]

            # s2 indicates if the qubit is active or idle 
            natureStatus = natureStatusList[processingBlock][qubit]

            # processing zone number?
            zoneNumber = zoneNumberList[processingBlock][qubit]
            
            # if the qubit is stored in idle zone 
            if zoneStatus == "i":

                # use the kiTbl for the position within the zone, corresponding to idle qubits 
                pointerQuadruple[qubit] = [zoneStatus, zoneNumber, positionInStorageZoneList[zoneNumber], natureStatus]

                # the next qubit has a position in the zone z that is one larger 
                positionInStorageZoneList[zoneNumber] += 1

                # and adjust the idle zone list accordingly 
                storageZoneQubits[zoneNumber].append(qubit)

            # if the qubit is stored in processing zone 
            else:

                # use position list corresponding to processing zones 
                pointerQuadruple[qubit] = [zoneStatus, zoneNumber, positionInProcessingZoneList[zoneNumber], natureStatus]

                # increase position by one 
                positionInProcessingZoneList[zoneNumber] += 1

                # append qubit in processing zone to Slist 
                processingZoneQubits[zoneNumber].append(qubit)

        
        # we create the new B iteratively, for each step in the Y list 
        processingBlockArrangement.append([processingZoneQubits, coveredGates, storageZoneQubits, pointerQuadruple])
    
    # return the new B list 
    return processingBlockArrangement




def computeArrangements(processingBlockArrangement, storageZoneSizes, maxProcessingZoneQubits):
    '''
    Given: 
        B: 
        storageZoneSizes: 
        maxProcessingZoneQubits: 
    Returns: 
        y: a list of Y positions for the qubits in the processing block s

    Given a list of processing blocks, this function returns a list of y positions for the qubits in these processing blocks. 
    The cost metric will be minimized with respect to a metric that quantifies the distances between qubits between layers. That's why we need y positions
    '''

    yPositionList = []

    for step in range(len(processingBlockArrangement)): 

        pointerQuadruple = processingBlockArrangement[step][3] 

        ySubList = []

        for q in range(len(pointerQuadruple)): 

            zoneStatus, zoneNumber, positionInZone, natureStatus = pointerQuadruple[q]
            
            if zoneStatus == 'p':
                # plot green node at position pos(processing zone 1) + q[2]
                tempYList = - storageZoneSizes[0] - zoneNumber* (storageZoneSizes[0] + maxProcessingZoneQubits) - positionInZone

                
            elif zoneStatus == 'i':
                # plot red node at position q[1] * pos(storage zone)
                tempYList = - zoneNumber *  (storageZoneSizes[0] + maxProcessingZoneQubits)  - positionInZone


            ySubList.append(tempYList)

        # y = y + y_sublist
        yPositionList.append(ySubList)

    return yPositionList



def computeTotalCost(yPositionList, nQ):
    '''
    Computes the cost of a given arrangement, characterised by the y positions of the qubits. 
    The rearrangement cost is computed based on a metric. 

    This metric shall guide us through the optimization process. 

    Given: 
        yPositionList:  A sequence of Y positions, corresponding to all the qubits in the circuit 
        nQ: Number of qubits in the circuit 

    Returns:
        totCost: total rearrangement cost (int), for the arrangement, given by cost metric in PDF
    '''

    numberProcessingBlocks = len(yPositionList)

    totCost = 0

    for processingBlock in range(1, numberProcessingBlocks):
        # print('step:', step)

        # look at layers step and step+1
        yPositionsCurrentBlock = yPositionList[processingBlock - 1]
        yPositionsNextBlock = yPositionList[processingBlock]

        # iterate over y positions in both layers 
        # if y position of the qi-th qubit in layer step-1 is not the same as of the qi-th qubit in layer step, add their y distance squared to the total cost 
        for qubitNo in range(nQ):
            totCost += (yPositionsCurrentBlock[qubitNo] - yPositionsNextBlock[qubitNo]) ** 2


    # return total cost 
    return totCost  





def updateStep(yPositionList, processingBlock, qubit1, qubit2, totCost):
    '''
    Given the list of Y positions and the layer number (step),
    this function returns a Y list that has qubits q1 and q2 exchanged (retuns only the part of the Y list that corresponds to the processing block) 
    in this layer and the updatet cost due to the swapping. 
    '''


    numberProcessingBlocks = len(yPositionList)

    newCost = totCost

    # if the layer of interest is not the leftmost layer 
    if processingBlock > 0: 

        # subtract the contribution to the total cost caused by the first and second qubit and their left neighbours 

        newCost -= (yPositionList[processingBlock][qubit1] - yPositionList[processingBlock - 1][qubit1]) ** 2 + (yPositionList[processingBlock][qubit2] - yPositionList[processingBlock - 1][qubit2]) ** 2

    # if the layer of interest is not the rightmost layer 
    if processingBlock < numberProcessingBlocks-1: 

        # subtract the contribution to the total cost caused by the first and second qubit and their right neighbours 
        newCost -= ( yPositionList[processingBlock][qubit1] - yPositionList[processingBlock+1][qubit1] ) ** 2 + (yPositionList[processingBlock][qubit2] - yPositionList[processingBlock+1][qubit2]) ** 2
    
    # swap qubits in layer
    temp = yPositionList[processingBlock][qubit1]
    yPositionList[processingBlock][qubit1] = yPositionList[processingBlock][qubit2]
    yPositionList[processingBlock][qubit2] = temp


    # add cost due to the new constellation of qubits, equal procedure as above. 
    if processingBlock > 0:
        newCost += (yPositionList[processingBlock][qubit1] - yPositionList[processingBlock - 1][qubit1])**2 + (yPositionList[processingBlock][qubit2] - yPositionList[processingBlock - 1][qubit2])**2

    if processingBlock < numberProcessingBlocks-1:
        newCost += (yPositionList[processingBlock][qubit1] - yPositionList[processingBlock + 1][qubit1])**2 + (yPositionList[processingBlock][qubit2] - yPositionList[processingBlock + 1][qubit2])**2

    # return only the part of the Y list that is of interest 
    return newCost, yPositionList[processingBlock]






'''

DISPLAYING

'''

def visualize_blocks(B, title):
    '''
    Given a list B, this function plots the qubits in the corresponding processing blocks. Same qubits are connected to each other between neighbouring layers. 
    The visualization is done for an arbitrary number of qubits, arranged in arbitrarily sized processing and storage zones. 
    Only constraint:    All processing and storage zones have to be equal in size, respectively. 
                        And the system has to be arranged like: 

                        Storage zone
                        Processing zone
                        Storage zone
                        Processing zone 
                        ...
                        Storage zone

    Accepts: 
        B:          List of interest in optimization procedure 
        title:      A title for the plot 
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
    for layerNumber in range(len(c_total)):

        # iterate over qubits in block 
        for qubitNumber in range(len(c_total[layerNumber])):

            # if in storage zone, add with corresponding label and zone keyword 
            if c_total[layerNumber][qubitNumber][0] == 'i':
                G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='storage', label=str(qubitNumber))

            # if in processing zone, add with corresponding label and zone keyword, remember: qbs can still be idle in processing zone, so we have to differentiate 
            elif c_total[layerNumber][qubitNumber][0] == 'p': 

                if c_total[layerNumber][qubitNumber][3] == 'i':
                    G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_idle', label=str(qubitNumber))

                elif c_total[layerNumber][qubitNumber][3] == 'a':
                    G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_active', label=str(qubitNumber))

    # assign positions to all the qubits 
    pos = {}

    lenProcessingZones =  len(B[0][0][0]) # corresponds to S list 
    print((B[0][0][0]))
    print(len(B[0][2][0]))
    # print(c_total[0])
    # print(c_total[0][2])
    lenStorageZones =  len(B[0][2][0]) # corresponds to F list 

    for node in G.nodes():

        # node is a tuple, node = (layer_number, node_number)
        layer_idx, node_idx = node
        
        # x position is just the layer number 
        x = layer_idx

        # depending if in storage, or processing zone, assign y coordinates 
        # storage zone 
        if c_total[layer_idx][node_idx][0] == 'i':
            y = c_total[layer_idx][node_idx][1]*- (lenStorageZones + lenProcessingZones) - c_total[layer_idx][node_idx][2]

        # processing zone 
        elif c_total[layer_idx][node_idx][0] == 'p':
            y = - lenStorageZones - (lenStorageZones + lenProcessingZones) *(c_total[layer_idx][node_idx][1]) - c_total[layer_idx][node_idx][2]

        # pos is a dictionary, pos((processingblock_number, qubit_number) = (x, y)). 
        # pos stores this for all the qubits in all the blocks 

        pos[node] = (x, y)


    # add edges 
    # We always add an edge between a qubit and the one in the layer next to it on the right. So, for the rightmost layer, we do not have to add an edge.
    for layerNumber in range(len(c_total)-1):
        for qubitNumber in range(len(c_total[layerNumber])):
            # current node is tuple
            current_node = (layerNumber, qubitNumber)

            # want to find the node in the layer next to it on the right that has the same label (corresponds to the same qubit)
            for qubitNumber_ in range(len(c_total[layerNumber+1])):

                # if we found the qubit with the same label 
                if G.nodes[current_node]['label'] == G.nodes[(layerNumber+1, qubitNumber_)]['label']:
                    next_node = (layerNumber + 1, qubitNumber_) 

                    # add an edge connecting these two nodes to the graph 
                    G.add_edge(current_node, next_node)

    # clarifying that the label keyword is actually the label that we want to use 
    node_labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    plt.figure(figsize=(10, 8))
    plt.title(title)
    nx.draw(G, pos, node_size=200, node_color=['red' if G.nodes[node]['zone'] == 'storage' else 'green' if G.nodes[node]['zone'] == 'processing_active' else 'blue' for node in G.nodes()], labels=node_labels, with_labels=True)
    
    # Add layer labels above nodes
    for layerNumber in range(len(c_total)):
        romanNumberList = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XII', 'XIII']
        layer_label = f'{romanNumberList[layerNumber]}'
        x = layerNumber
        y = max(pos[node][1] for node in pos if node[0] == layerNumber) + 0.7  # Adjust the y-coordinate for the label placement
        plt.text(x, y, layer_label, fontsize=12, ha='center', va='bottom')


    plt.show()    


# show arrangement of qubits after block aggregation
# visualize_blocks(processingBlockArrangement, 'Qubits arranged after block aggregation')


'''
ANIMATION
'''

def update(num, bList, title, ax):
    '''
    this function is used in the function animateSolving below
    Given a
    number of frames for the animation
    list of processingBlockArrangements - corresponding to certain swaps in the optimization algorithm procedure
    title
    and ax, a matplotlib object
    it creates the plot of the graph for every element in the processingBlockArrangementList 
    '''
    ax.clear()

    B = bList[num]
    
    if num < len(bList)-1:
        print('DEBUG: ', bList[num] == bList[num+1])

    # extract c from B
    c_total = []
    for i in range(len(B)):
        c_total.append(B[i][3])

    # Graph 
    G = nx.Graph() 

    

    # add nodes for all the qubits in the different layers 
    # every qubit gets assigned a zone keyword indicating in what zone it is and a label keyword indicating what number qubit it is. Also a layer number indicating what layer it is in. 

    # iterate over blocks 
    for layerNumber in range(len(c_total)):

        # iterate over qubits in block 
        for qubitNumber in range(len(c_total[layerNumber])):

            # if in storage zone, add with corresponding label and zone keyword 
            if c_total[layerNumber][qubitNumber][0] == 'i':
                G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='storage', label=str(qubitNumber))

            # if in storage zone, add with corresponding label and zone keyword, remember: qbs can still be idle in processing zone, so we have to differentiate 
            elif c_total[layerNumber][qubitNumber][0] == 'p': 

                if c_total[layerNumber][qubitNumber][3] == 'i':
                    G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_idle', label=str(qubitNumber))

                elif c_total[layerNumber][qubitNumber][3] == 'a':
                    G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_active', label=str(qubitNumber))


    # assign positions to all the qubits 
    pos = {}

    lenProcessingZones =  len(B[0][0][0]) # corresponds to S list 
    print((B[0][0][0]))
    print(len(B[0][2][0]))
    lenStorageZones =  len(B[0][2][0]) # corresponds to F list 

    for node in G.nodes():

        # node is a tuple, node = (layer_number, node_number)
        layer_idx, node_idx = node
        
        # x position is just the layer number 
        x = layer_idx

        # depending if in storage, or processing zone, assign y coordinates 
        # storage zone 
        if c_total[layer_idx][node_idx][0] == 'i':
            y = c_total[layer_idx][node_idx][1]*- (lenStorageZones + lenProcessingZones) - c_total[layer_idx][node_idx][2]

        # processing zone 
        elif c_total[layer_idx][node_idx][0] == 'p':
            y = - lenStorageZones - (lenStorageZones + lenProcessingZones) *(c_total[layer_idx][node_idx][1]) - c_total[layer_idx][node_idx][2]

        # pos is a dictionary, pos((processingblock_number, qubit_number) = (x, y)). 
        # pos stores this for all the qubits in all the blocks 

        pos[node] = (x, y)


    # add edges 
    # We always add an edge between a qubit and the one in the layer next to it on the right. So, for the rightmost layer, we do not have to add an edge.
    for layerNumber in range(len(c_total)-1):
        for qubitNumber in range(len(c_total[layerNumber])):
            # current node is tuple
            current_node = (layerNumber, qubitNumber)

            # want to find the node in the layer next to it on the right that has the same label (corresponds to the same qubit)
            for qubitNumber_ in range(len(c_total[layerNumber+1])):

                # if we found the qubit with the same label 
                if G.nodes[current_node]['label'] == G.nodes[(layerNumber+1, qubitNumber_)]['label']:
                    next_node = (layerNumber + 1, qubitNumber_) 

                    # add an edge connecting these two nodes to the graph 
                    G.add_edge(current_node, next_node)

    # clarifying that the label keyword is actually the label that we want to use 
    node_labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    # plt.figure(figsize=(10, 8))
    # plt.title(title)
    
    nx.draw(G, pos, node_size=200, node_color=['red' if G.nodes[node]['zone'] == 'storage' else 'green' if G.nodes[node]['zone'] == 'processing_active' else 'blue' for node in G.nodes()], labels=node_labels, with_labels=True)

    ax.set_title(title + ', progress: ' + str(int(100*num/len(bList))) + '%')




def animate_solving(bList, title):
    fig, ax = plt.subplots(figsize=(10,8))

    ani = animation.FuncAnimation(fig, update, frames=len(bList), interval=10, repeat=False, fargs= (bList, title, ax))
    plt.show()





def show_circuit_after_optimizing(BP, nQ, circ):
    '''
    This function uses qiskit to display a circuit with nQ qubits. The gates are displayed as dictated by the circ list created in the function random_circuit. 
    '''
    q_a = QuantumRegister(nQ, name='q')
    circuit = QuantumCircuit(q_a)
    for step in range(len(BP)):

        for g in range(len(BP[step][1][0])):

            # gate = layeredcirc[i][g][0]
            gate = BP[step][1][0][g]
            # print('test', gate)

            # q1 = circ[i][g][1][0]
            q1 = circ[gate][1][0]
            q2 = circ[gate][1][1]
            # q2 = circ[i][g][1][1]

            # circuit.cz(q_a[circ[gate][1][0]-1], q_a[circ[gate][1][1]-1], label=str(g+1))
            circuit.cz(q1, q2, label=str(gate+1))


        circuit.barrier()
    circuit.draw(output='mpl', justify='none', fold = 50)
    plt.title("Circuit arranged in layers \n")
    plt.show()
    # print(circuit)

# show_circuit_after_optimizing(processingBlockArrangement, NQ, circuitOfQubits)
# visualize_blocks(B, 'Visualizing Test')




