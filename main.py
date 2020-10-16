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
start = [0 for _ in range(len(crit_paths))]
offset = {}
mclm = {}
for i in node_loc:
    offset[i] = -1
    mclm[i] = True if i.func == 'Read' else False

while not_scheduled != 0:
    for dest in range(len(crit_paths)):
        crit = crit_paths[dest]
        for i in range(start[dest], len(crit)):
            if not alloc.check_pred(node_loc, pred[crit[i]]):
                break
            last_step = 0
            # NODE DELIVERY START
            if not alloc.are_pred_in_mclm(mclm, pred[crit[i]]):
                j = 1 if pred[crit[i]][0] == crit[i-1] else 0
                offset_step = max(offset[pred[crit[i]][1-j]] - abs(node_loc[pred[crit[i]][j]] - mins[dest]),
                                  offset[pred[crit[i]][j]])
                step = alloc.find_free_step(PEs, wires, node_loc[pred[crit[i]][j]], mins[dest], offset_step)
                alloc.schedule_nodes(PEs, wires, step, node_loc[pred[crit[i]][j]], mins[dest], configs, 1,
                                     pred[crit[i]][j])
                incr = abs(mins[dest]-node_loc[pred[crit[i]][j]])
                last_step = step + incr if incr > 0 else step + 1
            else:
                for j in range(len(pred[crit[i]])):
                    node = pred[crit[i]][j]
                    offset_step = max(offset[pred[crit[i]][1-j]] - abs(node_loc[node] - mins[dest]), offset[node])
                    offset_step = 0 if offset_step < 0 else offset_step
                    step = alloc.find_free_step(PEs, wires, node_loc[node], mins[dest], offset_step)
                    alloc.schedule_nodes(PEs, wires, step, node_loc[node], mins[dest], configs, j, node)
                    incr = step + abs(mins[dest] - node_loc[node])
                    incr = step + 1 if incr == step else incr
                    last_step = incr if incr > last_step else last_step
            # NODE DELIVERY END
            alloc.process_node(PEs, wires, last_step, len(graph[crit[i]]), mins[dest], configs)
            node_loc[crit[i]] = mins[dest]
            mclm[crit[i]] = True if len(graph[crit[i]]) > 1 else False
            offset[crit[i]] = last_step + 1
            not_scheduled -= 1
            start[dest] += 1

for i in range(len(PEs)):
    print("Step " + str(i))
    print(PEs[i])
    print(wires[i])
    print(configs[i].ccm1)
    print(configs[i].ccm3)

print(node_loc)
# print(crit_paths)
print(offset)