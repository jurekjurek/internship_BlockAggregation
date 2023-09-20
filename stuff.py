'''
If qiskit is not used for plotting 
'''

# QBpitch = 100       # distance between the different Qbit lines (y-dim)
# Gatepitch = 100     # distance between the different gates (x-dim)

# def QBy(q):
#     '''
#     returns y-coordinate of qubit line of qubit number q 
#     '''
#     return -(q - 1) * QBpitch

# def Gx(g):
#     '''
#     returns x-coordinate of gate g
#     '''
#     return g * Gatepitch

# print('B is now:')
# c_total = []
# for i in range(len(B)):
#     print('step', i)
#     print('SP:', B[i][0])
#     print('GP:', B[i][1])
#     print('FP:', B[i][2])
#     print('c:', B[i][3])
#     c_total.append(B[i][3])
#     print('\n')


def plot_and_print(B):
    # print('B is now:')
    c_total = []


    for i in range(len(B)):
        # print('step', i)
        # print('SP:', B[i][0])
        # print('GP:', B[i][1])
        # print('FP:', B[i][2])
        # print('c:', B[i][3])
        c_total.append(B[i][3])
        # print('\n')


    # print(c_total)

    x = 0
    y = 0

    node_groups = {}
    plt.figure()


    for layer in c_total: 
        for q_no in range(len(layer)):
            q = layer[q_no]

            number = str(q_no)  # Adding 1 to q_no to start numbering from 1

            if number in node_groups:
                node_groups[number].append((x, y))
            else:
                node_groups[number] = [(x, y)]

            if q[0] == 'p':
                # plot green node at position pos(processing zone 1) + q[2]
                y = -3 - q[2]
                if q[3] == 'i':
                    plt.scatter(x, y, color='blue', s=400)
                elif q[3] == 'a':
                    plt.scatter(x, y, color='green', s=400)
                plt.annotate(str(q_no), (x, y), ha='center', va='center')

                # print('p')
            elif q[0] == 'i':
                # plot red node at position q[1] * pos(storage zone)
                y = q[1]*-7 - q[2]
                plt.scatter(x, y, color='red', s=400)
                plt.annotate(str(q_no), (x, y), ha='center', va='center')

                # print('s')
            

            # shift position of plotting to the right 
        x += 1

    # for number, positions in node_groups.items():
    #     sorted_positions = sorted(positions, key=lambda pos: pos[1])
    #     x_values, y_values = zip(*sorted_positions)
    #     plt.plot(x_values, y_values, marker='o', label=f'Node {number}')

    # Connect nodes between neighboring layers
    for i in range(len(c_total) - 1):
        for number, positions in node_groups.items():
            current_layer_positions = [(pos[0], pos[1]) for pos in positions if pos[0] == i]
            next_layer_positions = [(pos[0], pos[1]) for pos in positions if pos[0] == i + 1]

            for pos1 in current_layer_positions:
                closest_pos2 = min(next_layer_positions, key=lambda pos2: abs(pos2[1] - pos1[1]))
                plt.plot([pos1[0], closest_pos2[0]], [pos1[1], closest_pos2[1]], color='black')

    plt.title('Qubits arranged in Processing zones \n')
    plt.axis('off')
    plt.show()

# plot_and_print(B)




'''
Tabu search stuff 
'''


# def reconstructBlocksFromArrangements(BP, Fsizes, Qmax, Mmax, Nq, Y, zonesTbl, s1Tbl, s2Tbl):
#     '''
#     Returns: 
#         bNew: an updatet B-list 
#     '''

#     bNew = []

#     qbTbl = [q for q in range(Nq)]

#     for step in range(len(Y)):
        
#         qbTblSort = qbTbl


#         # GP = BP[step][1]


#         SPNew = [[[], []] for m in range(Mmax)]

#         FPNew = [[] for f in range(len(Fsizes))]

#         cNew = [[] for q in range(Nq)]

#         kpTbl = [1] * Mmax

#         kiTbl = [1] * len(Fsizes)


#         for qi in range(Nq):
#             q = qbTblSort[qi]
#             s1 = s1Tbl[step][q]
#             s2 = s2Tbl[step][q]

#             z = zonesTbl[step][q]

#             if s1 == 'i':
#                 cNew[q] = [s1, z, kiTbl[z], s2]

#                 kiTbl[z] += 1

#                 FPNew[z] = FPNew[z] + q 

#             else: 
#                 cNew[q] = [s1, z, kpTbl[z], s2]

#                 kpTbl[z] += 1

#                 if s2 == 'a':
#                     SPNew[z][1].append(q)
#                 else: 
#                     SPNew[z][2].append(q)


#     return bNew


'''

'''

def animate_solving(bList, title):
    '''
    This function animates a solving process given a list of Bs in the course of the iterations 
    '''

    fig, ax = plt.subplots()

    artists = []
    # container = []

    for i in range(len(bList)):

        B = bList[i]

        container = []

        # extract c from B
        c_total = []
        for j in range(len(B)):
            c_total.append(B[j][3])

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

                # print(G.nodes())

        # assign positions to all the qubits 
        pos = {}

        lenProcessingZones =  len(B[0][0][0]) # corresponds to S list 
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
        # plt.figure(figsize=(10, 8))
        plt.title(title + ', iteration' + str(i))
        nx.draw(G, pos, node_size=200, node_color=['red' if G.nodes[node]['zone'] == 'storage' else 'green' if G.nodes[node]['zone'] == 'processing_active' else 'blue' for node in G.nodes()], labels=node_labels, with_labels=True)
        
        # Add layer labels above nodes
        # for layer_no in range(len(c_total)):
        #     layer_label = f'B{layer_no + 1}'
        #     x = layer_no
        #     y = max(pos[node][1] for node in pos if node[0] == layer_no) + 0.7  # Adjust the y-coordinate for the label placement
        #     plt.text(x, y, layer_label, fontsize=12, ha='center', va='bottom')


        # Collect artists for the frame
        frame_artists = ax.findobj()
        container.extend(frame_artists)  # Extend the container with the artists for this frame



        artists.append(container.copy())

        # container = 
        # artists.append(frame_artists)
        print('appended' + str(i))

       

    for k in range(len(artists)):
        if k < len(artists)-1:
            print(artists[k] == artists[k+1])

    print(np.shape(artists)) 
    artists = np.array(artists)

    artists = artists.flatten()

    ani = animation.ArtistAnimation(fig=fig, artists=artists, interval=40)
    plt.show()

    # return None



'''
Was in blockaggreation.py
'''

            # zoneCtr = 1
            # gateCoverage = 0



            # # essentially the same as is done in EvaulateGateCoverage???


            # # evaluate the gate coverage for this specific constellation of sets 
            # for qubitSetNumber in range(len(gatesCovered)):
            #     if len(processingZoneQubits[qubitSetNumber]) < qMax and zoneCtr <= mMax:
            #         gateCoverage += len(gatesCovered[qubitSetNumber])
            #         zoneCtr += 1





'''
aus letzter fct in block_aggregation.py
'''

            # iterate over the gates in the gates sets corresponding to qubit sets in the processing zones 
            # for gi in range(len(GP[gpi])):

                # print(cRaw[gi][0], GP[gpi][gi])

                # Remove the covered gate from the circuit
                # for k in range(len(cRaw)):
                    # if cRaw[k][0] == GP[gpi][gi]:
                # cRaw.pop(GP[gpi][gi])    
                # break
                # cRaw = [x for x in cRaw if x != GP[gpi][gi]]


'''
First try animation function
'''


# def animate_solving(bList, title):
#     '''
#     This function animates a solving process given a list of Bs in the course of the iterations 
#     '''

#     fig, ax = plt.subplots()

#     artists = []
#     # container = []

#     for i in range(len(bList)):

#         B = bList[i]

#         container = []

#         # extract c from B
#         c_total = []
#         for j in range(len(B)):
#             c_total.append(B[j][3])

#         # Graph 
#         G = nx.Graph() 

        

#         # add nodes for all the qubits in the different layers 
#         # every qubit gets assigned a zone keyword indicating in what zone it is and a label keyword indicating what number qubit it is. Also a layer number indicating what layer it is in. 

#         # iterate over blocks 
#         for layerNumber in range(len(c_total)):

#             # iterate over qubits in block 
#             for qubitNumber in range(len(c_total[layerNumber])):

#                 # if in storage zone, add with corresponding label and zone keyword 
#                 if c_total[layerNumber][qubitNumber][0] == 'i':
#                     G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='storage', label=str(qubitNumber))

#                 # if in storage zone, add with corresponding label and zone keyword, remember: qbs can still be idle in processing zone, so we have to differentiate 
#                 elif c_total[layerNumber][qubitNumber][0] == 'p': 

#                     if c_total[layerNumber][qubitNumber][3] == 'i':
#                         G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_idle', label=str(qubitNumber))

#                     elif c_total[layerNumber][qubitNumber][3] == 'a':
#                         G.add_node((layerNumber, qubitNumber), layer=layerNumber, zone='processing_active', label=str(qubitNumber))

#                 # print(G.nodes())

#         # assign positions to all the qubits 
#         pos = {}

#         lenProcessingZones =  len(B[0][0][0]) # corresponds to S list 
#         lenStorageZones =  len(B[0][2][0]) # corresponds to F list 

#         for node in G.nodes():

#             # node is a tuple, node = (layer_number, node_number)
#             layer_idx, node_idx = node
            
#             # x position is just the layer number 
#             x = layer_idx

#             # depending if in storage, or processing zone, assign y coordinates 
#             # storage zone 
#             if c_total[layer_idx][node_idx][0] == 'i':
#                 y = c_total[layer_idx][node_idx][1]*- (lenStorageZones + lenProcessingZones) - c_total[layer_idx][node_idx][2]

#             # processing zone 
#             elif c_total[layer_idx][node_idx][0] == 'p':
#                 y = - lenStorageZones - (lenStorageZones + lenProcessingZones) *(c_total[layer_idx][node_idx][1]) - c_total[layer_idx][node_idx][2]

#             # pos is a dictionary, pos((processingblock_number, qubit_number) = (x, y)). 
#             # pos stores this for all the qubits in all the blocks 

#             pos[node] = (x, y)


#         # add edges 
#         # We always add an edge between a qubit and the one in the layer next to it on the right. So, for the rightmost layer, we do not have to add an edge.
#         for layerNumber in range(len(c_total)-1):
#             for qubitNumber in range(len(c_total[layerNumber])):
#                 # current node is tuple
#                 current_node = (layerNumber, qubitNumber)

#                 # want to find the node in the layer next to it on the right that has the same label (corresponds to the same qubit)
#                 for qubitNumber_ in range(len(c_total[layerNumber+1])):

#                     # if we found the qubit with the same label 
#                     if G.nodes[current_node]['label'] == G.nodes[(layerNumber+1, qubitNumber_)]['label']:
#                         next_node = (layerNumber + 1, qubitNumber_) 

#                         # add an edge connecting these two nodes to the graph 
#                         G.add_edge(current_node, next_node)

#         # clarifying that the label keyword is actually the label that we want to use 
#         node_labels = {node: G.nodes[node]['label'] for node in G.nodes()}
#         # plt.figure(figsize=(10, 8))
#         plt.title(title + ', iteration' + str(i))
#         nx.draw(G, pos, node_size=200, node_color=['red' if G.nodes[node]['zone'] == 'storage' else 'green' if G.nodes[node]['zone'] == 'processing_active' else 'blue' for node in G.nodes()], labels=node_labels, with_labels=True)
        
#         # Add layer labels above nodes
#         # for layerNumber in range(len(c_total)):
#         #     layer_label = f'B{layerNumber + 1}'
#         #     x = layerNumber
#         #     y = max(pos[node][1] for node in pos if node[0] == layerNumber) + 0.7  # Adjust the y-coordinate for the label placement
#         #     plt.text(x, y, layer_label, fontsize=12, ha='center', va='bottom')


#         # Collect artists for the frame
#         frame_artists = ax.findobj()
#         container.extend(frame_artists)  # Extend the container with the artists for this frame



#         artists.append(container.copy())

#         # container = 
#         # artists.append(frame_artists)
#         print('appended' + str(i))

       

#     for k in range(len(artists)):
#         if k < len(artists)-1:
#             print(artists[k] == artists[k+1])

#     print(np.shape(artists)) 
#     artists = np.array(artists)

#     artists = artists.flatten()

#     ani = animation.ArtistAnimation(fig=fig, artists=artists, interval=40)
#     plt.show()

#     # return None


'''
intabusearch firstf unction
'''


                # KOKOLORES
                # if it is an active qubit in a processing zone 
                # if s2 == "a":

                #     # store it in the first position in the SPnew list S = [[active, idle], [active, idle] ... , [active, idle]]
                #     SPnew[z][0][0].append(q)

                # # if it is an idle qubit in a processing zone 
                # else:

                #     # store it in the according position 
                #     SPnew[z][0][1].append(q)




'''
in alternatingOptimization
'''

        # still needs to be returned by tabusearch 
        # if the minimal cost obtained by the tabu search is smaller than the best cost so far, replace the best cost with the Tabu Search one. 
        # if bestCostUpdateAll[-1] < costTotBest:

        #     if visualOutput == True: 
        #         print('visualoutput')

        #     # last element in list 
        #     costTotBest = bestCostUpdateAll[-1]