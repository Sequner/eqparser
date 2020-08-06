from classes import *


def assign_locations(dfg, n):
    inputs = {}
    for i in dfg:
        if i.func == 'Read':
            inputs[i] = 0
    batch = int((len(inputs)-1)/n)
    counter1 = 0
    counter2 = 0
    for i in dfg:
        if i in inputs:
            inputs[i] = counter2
            if counter1 == batch:
                counter2 += 1
                counter1 = 0
            else:
                counter1 += 1
        else:
            inputs[i] = -1
    return inputs


def is_path_set(pos, x):
    for i in pos:
        if i != x:
            return False
    return True


def free_all_pe(pes):
    for i in range(len(pes)):
        pes[i].wire.is_busy = False


def print_pes_status(pes):
    status = []
    for i in pes:
        status.append(i.wire.is_busy)
    print(status)


def are_inputs_ready(node_pos, nodes, x):
    if not node_pos or not nodes[0] in node_pos or not nodes[1] in node_pos:
        return False
    if node_pos[nodes[0]] == x and node_pos[nodes[1]] == x:
        return True
    return False


def find_linear_m(crit_paths, node_pos_orig, pred, n):
    mins = []
    for crit in crit_paths:
        PEs = [PE(i, [], Wire(i, False), None, False) for i in range(n)]
        for i in node_pos_orig:
            if node_pos_orig[i] != -1:
                if len(PEs[node_pos_orig[i]].inputs) <= 2:
                    PEs[node_pos_orig[i]].inputs.append(i)
        min_m = 1000
        min_steps = 1000
        min_x = 0
        for x in range(n):
            if x in mins:
                continue
            m = 0
            steps = 0
            crit_pos = [-1 for i in range(len(crit))]
            node_pos = dict(node_pos_orig)
            while not is_path_set(crit_pos, x):  # Check if all nodes in crit path are set
                for i in range(len(crit)):  # Perform operation in PE if correct inputs are given
                    index = crit[i]
                    if node_pos[index] != -1:
                        continue
                    if are_inputs_ready(node_pos, pred[index], x) or (i > 0 and node_pos[crit[i - 1]] == x):
                        PEs[x].operation = index
                        crit_pos[i] = x

                for i in crit:  # Choose node from crit path to allocate
                    for j in pred[i]:  # Choose predecessor
                        if node_pos[j] == -1:  # If predecessor is not allocated yet -> ignore it
                            continue
                        if node_pos[j] < x:  # If pred 'j' is located on the left size of PE 'x'
                            if not (PEs[node_pos[j]].wire.is_busy or PEs[node_pos[j] + 1].wire.is_busy):  # if PE j+1 and PE of 'j' are free
                                if node_pos[j] + 1 == x:  # If PE of 'j' and PE 'x' are neighbours
                                    for k in range(len(PEs[x].inputs)):  # Insert into node inputs
                                        if PEs[x].inputs[k] not in pred[i]:
                                            PEs[x].inputs[k] = j
                                PEs[node_pos[j]].wire.is_busy = True
                                PEs[node_pos[j] + 1].wire.is_busy = True
                                node_pos[j] += 1
                                m += 1
                        elif node_pos[j] > x:  # If pred 'j' is located on the left size of PE 'x'
                            if not (PEs[node_pos[j]].wire.is_busy or PEs[node_pos[j] - 1].wire.is_busy):  # if PE j+1 and PE of 'j' are free
                                if node_pos[j] - 1 == x:  # If PE of 'j' and PE 'x' are neighbours
                                    for k in range(len(PEs[x].inputs)):  # Insert into node inputs
                                        if PEs[x].inputs[k] not in pred[i]:
                                            PEs[x].inputs[k] = j
                                PEs[node_pos[j]].wire.is_busy = True
                                PEs[node_pos[j]-1].wire.is_busy = True
                                node_pos[j] -= 1
                                m += 1
                for i in range(len(PEs)):  # Output result of operation
                    if PEs[i].operation:
                        node_pos[PEs[i].operation] = x
                        PEs[i].operation = None
                steps += 1
                free_all_pe(PEs)
            if min_m > m or (min_m == m and min_steps > steps):
                min_m = m
                min_steps = steps
                min_x = x
        mins.append(min_x)
    return mins


def find_transf(transf, list):
    for i in list:
        print('kek')