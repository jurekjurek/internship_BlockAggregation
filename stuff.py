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



