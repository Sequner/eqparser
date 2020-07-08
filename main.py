import eqparser
import dfg
import alloc
from classes import *

# 1) Equation must be in form "Variable=some arithmetic"
# 2) There must be no SPACE-s in equation
eq = "z=a+b*c-d"
graph = eqparser.get_graph(eq)
# Graph output
eqparser.print_graph(graph)
# E = dfg.asap(graph)
# for node in E:
#     print("E of " + str(node) + " -> " + str(E[node]))
#
# T = max(E.values())
# L = dfg.alap(graph, T)
# for node in L:
#     print("L of " + str(node) + " -> " + str(L[node]))
#
# crit = dfg.find_crit_path(graph)
# new = dfg.remove_path(graph, crit)
# print(new)
#
# # Enter number of PEs available
# # Assumed that number of variables is at most twice as large as number of PEs
# n = 4
# # wires = [Wire(i, False) for i in range(n)]
# max = 0
# node_pos = alloc.assign_inputs(graph, n)
# PEs = [PE(i, [dfg.list_inputs(graph)[i]], Wire(i, False), None, False) for i in range(n)]
# for j in range(n):
#     for i in range(len(crit)):
#         while
