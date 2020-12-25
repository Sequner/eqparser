from classes import *


def assign_locations(dfg, n):
    inputs = {}
    for i in dfg:
        if i.func == 'Read':
            inputs[i] = 0
    len_inp = len(inputs)
    slot = 0
    counter = 0
    for i in dfg:
        if i in inputs:
            if len_inp > n:
                inputs[i] = slot
                counter += 1
                len_inp -= 1
                if counter > 1:
                    slot += 1
                    counter = 0
                    n -= 1
            else:
                inputs[i] = slot
                slot += 1
        else:
            inputs[i] = -1
    return inputs


def is_path_set(pos, x):
    for i in pos:
        if i != x:
            return False
    return True


def find_free_step(pes, wires, x, y, start):
    to_set = -1
    step = start
    if x < y:
        while to_set == -1:
            for i in range(step, step+y-x):
                if i >= len(pes):
                    to_set = step
                    break
                elif wires[i][x+i-step] or wires[i][x+i-step+1]:
                    break
                elif i == step and pes[i][x+i-step]:  # i-step = 0
                    break
                elif i == step+y-x-1 and not pes[i][x+i-step+1]:  # x+i-step+1 = y
                    to_set = step
            step += 1
    elif x > y:
        while to_set == -1:
            for i in range(step, step+x-y):
                if i >= len(pes):
                    to_set = step
                    break
                elif wires[i][x-(i-step)] or wires[i][x-(i-step)-1]:
                    break
                elif i == step and pes[i][x-(i-step)]:
                    break
                elif i == step+x-y-1 and not pes[i][x-(i-step)-1]:
                    to_set = step
            step += 1
    else:
        for i in range(start, len(pes)):
            if not pes[i][x]:
                return i
        return len(pes)
    return to_set


def schedule_nodes(pes, wires, step, x, y, config, slot, node):
    if x < y:
        for i in range(step, step+y-x):
            if i < len(pes):
                wires[i][x+i-step] = True
                wires[i][x+i-step+1] = True
                config[i].ccm6[x+i-step] = "through"
                config[i].ccm6[x+i-step+1] = "through"
            else:
                pes.append([False for _ in range(len(pes[0]))])
                wires.append([True if z == x+i-step or z == x+i-step+1 else False for z in range(len(pes[0]))])
                config.append(Config(len(pes[0])))
                config[-1].ccm6[x+i-step] = "through"
                config[-1].ccm6[x+i-step+1] = "through"
        pes[step][x] = True
        pes[step+y-x-1][y] = True
        config[step].ccm1[x] = "reading node " + str(node)
        config[step].ccm6[x] = "out"
        config[step+y-x-1].ccm6[y] = "in"
    elif x > y:
        for i in range(step, step+x-y):
            if i < len(pes):
                wires[i][x-(i-step)] = True
                wires[i][x-(i-step)-1] = True
                config[i].ccm6[x-(i-step)] = "through"
                config[i].ccm6[x-(i-step)-1] = "through"
            else:
                pes.append([False for _ in range(len(pes[0]))])
                wires.append([True if z == x-(i-step) or z == x-(i-step)-1 else False for z in range(len(pes[0]))])
                config.append(Config(len(pes[0])))
                config[-1].ccm6[x-(i-step)] = "through"
                config[-1].ccm6[x-(i-step)-1] = "through"
        pes[step][x] = True
        pes[step+x-y-1][y] = True
        config[step].ccm1[x] = "reading node " + str(node)
        config[step].ccm6[x] = "out"
        config[step+x-y-1].ccm6[y] = "in"
    else:
        if step < len(pes):
            pes[step][x] = True
        else:
            pes.append([True if i == x else False for i in range(len(pes[0]))])
            wires.append([False for _ in range(len(pes[0]))])
            config.append(Config(len(pes[0])))
        config[step].ccm1[x] = "reading node " + str(node)
        config[step].ccm3[x] = "intoDPR" + str(slot+2)


def process_node(pes, wires, step, succ_num, pe_num, config):
    if step < len(pes):
        pes[step][pe_num] = True
    else:
        pes.append([False if x != pe_num else True for x in range(len(pes[0]))])
        wires.append([False for _ in range(len(pes[0]))])
        config.append(Config(len(pes[0])))
    if succ_num > 1:
        config[step].ccm5[pe_num] = "intoMem"
    else:
        config[step].ccm3[pe_num] = "intoDPR2"


def are_pred_in_mclm(nodes, pred):
    t1 = t2 = False
    for i in nodes:
        for j in i:
            t1 = True if j == pred[0] else t1
            t2 = True if j == pred[1] else t2
    return t1 and t2


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


def check_pred(nodes_set, pred):
    for node in pred:
        if nodes_set[node] == -1:
            return False
    return True


def are_free(pe1, pe2):
    if pe1.wire.is_busy or pe2.wire.is_busy or pe1.operation or pe2.operation:
        return False
    return True
