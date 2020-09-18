import eqparser
import dfg
import alloc
from classes import *


# 1) Equation must be in form "Variable=some arithmetic"
# 2) There must be no SPACE-s in equation
eq = "z=a*c+e+(c-d)-c+((c-d)/(a+b)+(a*c+e+(c-d)))"
graph = eqparser.get_graph(eq)
print(graph)
# Graph output
# eqparser.print_graph(graph)

# Crit path extraction
crit_paths = dfg.find_crit_paths(graph)
print(crit_paths)
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

PEs = [[False for x in range(n)]]
wires = [[False for x in range(n)]]
configs = [Config(n)]

crit_pe_inputs = [[] for x in range(len(crit_paths))]
mclm = [[] for x in range(n)]
step_node_set = {}
start = [0 for x in range(len(crit_paths))]

while not_scheduled != 0:
    for dest in range(len(crit_paths)):
        crit = crit_paths[dest]
        for i in range(len(crit)):
            if node_loc[crit[i]] != -1:
                continue
            if not alloc.check_pred(node_loc, pred[crit[i]]):
                break
            last_step = 0
            # NODE DELIVERY START
            if i > 0:
                j = 1 if pred[crit[i]][0] == crit[i-1] else 0
                start[dest] -= abs(node_loc[pred[crit[i]][j]] - mins[dest]) - 2
                step = alloc.find_free_step(PEs, wires, node_loc[pred[crit[i]][j]], mins[dest], start[dest])
                alloc.schedule_nodes(PEs, wires, step, node_loc[pred[crit[i]][j]], mins[dest], configs, 1, pred[crit[i]][j])
                incr = abs(mins[dest]-node_loc[pred[crit[i]][j]])
                last_step = step + incr if incr > 0 else step + 1
            else:
                for j in range(len(pred[crit[i]])):
                    node = pred[crit[i]][j]
                    step = alloc.find_free_step(PEs, wires, node_loc[node], mins[dest], start[dest])
                    alloc.schedule_nodes(PEs, wires, step, node_loc[node], mins[dest], configs, j, node)
                    incr = step + abs(mins[dest] - node_loc[node])
                    incr = step + 1 if incr == step else incr
                    last_step = incr if incr > last_step else last_step
            # NODE DELIVERY END
            alloc.process_node(PEs, wires, last_step, len(graph[crit[i]]), mins[dest], configs)
            start[dest] = last_step + 1 if len(graph[crit[i]]) > 1 else last_step
            not_scheduled -= 1
            node_loc[crit[i]] = mins[dest]

for i in range(len(PEs)):
    print("Step " + str(i))
    print(PEs[i])
    print(wires[i])
    print(configs[i].ccm1)
    print(configs[i].ccm3)
print(node_loc)