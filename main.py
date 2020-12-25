import eqparser
import dfg
import alloc
from classes import *


# 1) Equation must be in form "Variable=some arithmetic"
# 2) There must be no SPACE-s in the equation
eq1 = "y00=F00*0+F01*0+F02*0+F10*0+F11*X00+F12*X01+F20*0+F21*X10+F22*X11"
eq2 = "y01=F00*0+F01*0+F02*0+F10*X00+F11*X01+F12*X02+F20*X10+F21*X11+F22*X12"
eq3 = "y02=F00*0+F01*0+F02*0+F10*X01+F11*X02+F12*X03+F20*X11+F21*X12+F22*X13"
eq4 = "y10=F00*0+F01*X00+F02*X01+F10*0+F11*X10+F12*X11+F20*0+F21*X20+F22*X21"
eq5 = "y11=F00*X00+F01*X01+F02*X02+F10*X10+F11*X11+F12*X12+F20*X20+F21*X21+F22*X22"
eq6 = "y12=F00*X01+F01*X02+F02*X03+F10*X11+F11*X12+F12*X13+F20*X21+F21*X22+F22*X23"
eq7 = "y20=F00*0+F01*X10+F02*X11+F10*0+F11*X20+F12*X21+F20*0+F21*X30+F22*X31"
eq8 = "y21=F00*X10+F01*X11+F02*X12+F10*X20+F11*X21+F12*X22+F20*X30+F21*X31+F22*X32"
eq9 = "y22=F00*X11+F01*X12+F02*X13+F10*X21+F11*X22+F12*X23+F20*X31+F21*X32+F22*X33"
eq = [eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8, eq9]
graph = eqparser.get_graph(eq1)
# Graph output
# eqparser.print_graph(graph)

# Crit path extraction
crit_paths = dfg.find_crit_paths(graph)
# Enter number of PEs available
# Assumed that number of variables is at most twice as large as number of PEs
n = len(crit_paths)
node_loc = alloc.assign_locations(graph, n)
print(node_loc)
pred = dfg.find_pred(graph)
mins = alloc.find_linear_m(crit_paths, node_loc, pred, n)

not_scheduled = 0
for i in graph:
    if not (i.func == 'Read' or i.func == 'Write'):
        not_scheduled += 1

PEs = [[False for _ in range(n)]]
wires = [[False for _ in range(n)]]
configs = [Config(n)]
start = [0 for _ in range(len(crit_paths))]
offset = {}
mclm = [[] for _ in range(n)]
for i in node_loc:
    offset[i] = -1
    nd = node_loc[i]
    if nd >= 0:
        mclm[nd].append(i)

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
            if len(graph[crit[i]]) > 1:
                mclm[mins[dest]].append(crit[i])
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
print(mclm)