from classes import *


def asap(dfg):
    pred = find_pred(dfg)
    E = {}
    for i in dfg:
        if not pred[i]:
            E[i] = 1

    while len(E) != len(dfg):
        for node in dfg:
            if node in E:
                continue
            if all_nodes_sched(pred[node], E):
                E[node] = max_stage(pred[node], E) + 1
    return E


def alap(dfg, T):
    L = {}
    for i in dfg:
        if not dfg[i]:
            L[i] = T

    while len(L) != len(dfg):
        for node in dfg:
            if node in L:
                continue
            if all_nodes_sched(dfg[node], L):
                print(node)
                L[node] = min_stage(dfg[node], L) - 1
    return L


def all_nodes_sched(nodes, e):
    for node in nodes:
        if not node in e:
            return False
    return True


def max_stage(nodes, e):
    mx = 0
    for node in nodes:
        if e[node] > mx:
            mx = e[node]
    return mx


def min_stage(nodes, l):
    mn = l[nodes[0]]
    for node in nodes:
        if l[node] < mn:
            mn = l[node]
    return mn


def find_pred(dfg):
    pred = {}
    for i in dfg:
        pred[i] = []
    for i in dfg:
        for j in dfg[i]:
            pred[j].append(i)
    return pred


def find_crit_path(dfg):
    inputs = []
    for i in dfg:
        if i.func == 'Read':
            inputs.append(i)
    crit = []
    for i in inputs:
        traversed = {i: 0}
        stack = [i]
        while stack:
            if not dfg[stack[-1]]:
                if len(stack) > len(crit):
                    crit = stack[:]  # copying list
            if traversed[stack[-1]] == len(dfg[stack[-1]]):
                stack.pop()
                if stack:
                    traversed[stack[-1]] += 1
            else:
                stack.append(dfg[stack[-1]][traversed[stack[-1]]])
                traversed[stack[-1]] = 0
    if crit[-1].func == 'Write':
        return crit[1:len(crit)-1]
    return crit[1:]


def find_crit_paths(dfg):
    crit = find_crit_path(dfg)
    new = remove_path(dfg, crit)
    crits = []
    while crit:
        crits.append(crit)
        crit = find_crit_path(new)
        new = remove_path(new, crit)
    return crits


def remove_path(dfg, path):
    graph = dict(dfg)
    for i in path:
        if i in graph:
            graph.pop(i)
    new = {}
    for i in graph:
        new[i] = []
        for j in graph[i]:
            if j in graph:
                new[i].append(j)
    return new


def change_pred(node1, node2, pred):
    for i in pred:
        if i == node1 or i == node2:
            continue
        for j in range(len(pred[i])):
            if node2 == pred[i][j]:
                pred[i][j] = node1


def remove_node(node, pred, dfg):
    dfg.pop(node)
    for i in pred:
        dfg[i].remove(node)