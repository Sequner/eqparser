import eqparser
import dfg
import alloc
from classes import *


# 1) Equation must be in form "Variable=some arithmetic"
# 2) There must be no SPACE-s in equation
eq = "z=a+(b*(c+d)+(a+b))-b"
graph = eqparser.get_graph(eq)
print(graph)
# Graph output
# eqparser.print_graph(graph)

# Crit path extraction
crit_paths = dfg.find_crit_paths(graph)

# Enter number of PEs available
# Assumed that number of variables is at most twice as large as number of PEs
n = 4
node_loc = alloc.assign_locations(graph, n)
pred = dfg.find_pred(graph)
mins = alloc.find_linear_m(crit_paths, node_loc, pred, n)

not_scheduled = 0
for i in graph:
    if not (i.func == 'Read' or i.func == 'Write'):
        not_scheduled += 1

steps = 0
transfers = [{} for i in range(n)]
PEs = [PE(i, [], Wire(i, False), None, False) for i in range(n)]
for i in node_loc:
    if node_loc[i] != -1:
        if len(PEs[node_loc[i]].inputs) <= 2:
            PEs[node_loc[i]].inputs.append(i)
print(crit_paths)
while not_scheduled > 0:
    for dest in range(len(crit_paths)):
        crit = crit_paths[dest]
        for i in range(len(crit)):  # Perform operation in PE if correct inputs are given
            index = crit[i]
            if node_loc[index] != -1:
                continue
            if alloc.are_inputs_ready(transfers[mins[dest]], pred[index], mins[dest]):
                PEs[mins[dest]].operation = index
                not_scheduled -= 1
        for i in crit:  # Choose node from crit path to allocate
            for j in pred[i]:  # Choose predecessor
                if node_loc[j] == -1:  # If predecessor is not allocated yet -> ignore it
                    continue
                if j not in transfers[mins[dest]]:
                    transfers[mins[dest]][j] = node_loc[j]
                node_pos = transfers[mins[dest]][j]
                if node_pos < mins[dest]:  # If pred 'j' is located on the left size of PE 'x'
                    if not (PEs[node_pos].wire.is_busy or PEs[node_pos+1].wire.is_busy):  # if PE j+1 and PE of 'j' are free
                        if node_pos + 1 == mins[dest]:  # If PE of 'j' and PE 'x' are neighbours
                            for k in range(len(PEs[mins[dest]].inputs)):  # Insert into node inputs
                                if PEs[mins[dest]].inputs[k] not in pred[i]:
                                    PEs[mins[dest]].inputs[k] = j
                        PEs[node_pos].wire.is_busy = True
                        PEs[node_pos+1].wire.is_busy = True
                        transfers[mins[dest]][j] += 1
                elif node_pos > mins[dest]:  # If pred 'j' is located on the left size of PE 'x'
                    if not (PEs[node_pos].wire.is_busy or PEs[node_pos-1].wire.is_busy):  # if PE j+1 and PE of 'j' are free
                        if node_pos-1 == mins[dest]:  # If PE of 'j' and PE 'x' are neighbours
                            for k in range(len(PEs[mins[dest]].inputs)):  # Insert into node inputs
                                if PEs[mins[dest]].inputs[k] not in pred[i]:
                                    PEs[mins[dest]].inputs[k] = j
                        PEs[node_pos].wire.is_busy = True
                        PEs[node_pos-1].wire.is_busy = True
                        transfers[mins[dest]][j] -= 1
        for i in range(len(PEs)):  # Output result of operation
            if PEs[i].operation:
                node_loc[PEs[i].operation] = mins[dest]
                transfers[mins[dest]][PEs[i].operation] = mins[dest]
                PEs[i].operation = None
    steps += 1
    print(steps)
    print(node_loc)
    print(transfers)
    print(PEs)
    alloc.free_all_pe(PEs)
print(steps)
