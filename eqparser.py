from classes import *
import dfg

def get_graph(eq):
    nxt = [-1 for x in eq]  # array that will store the sequence of dfg
    # elements with value -1 are not included in dfg except 1st element
    stack = []
    for i in range(2, len(eq)):
        char = eq[i]
        if char not in "+-*/()":
            if eq[i-1] == '(' or eq[i-1] == '=':
                nxt[i] = i + 1
            elif eq[i-1] == '*' or eq[i-1] == '/' or i == len(eq) - 1:
                nxt[i] = i - 1
            elif eq[i+1] == '*' or eq[i+1] == '/':
                nxt[i] = i + 1
            else:
                nxt[i] = i - 1
            if i == len(eq) - 1:
                nxt[stack.pop()] = 0
        else:
            if eq[i] == '(':
                continue
            elif not stack:
                stack.append(i)
            elif eq[i - 2] == '(':
                stack.append(i)
            elif eq[i] != ')':
                if eq[i] == '+' or eq[i] == '-':
                    nxt[stack.pop()] = i
                    stack.append(i)
                else:
                    if i+2 == len(eq):
                        if eq[stack[-1]] in '+-':
                            nxt[i] = stack[-1]
                        else:
                            nxt[stack.pop()] = i
                            stack.append(i)
                    elif eq[i+2] in '*/':
                        if eq[stack[-1]] in '*/':
                            nxt[stack.pop()] = i
                        stack.append(i)
                    else:
                        if eq[stack[-1]] in '*/':
                            nxt[stack.pop()] = i
                        if stack:
                            nxt[i] = stack[-1]
                        if eq[i+1] == '(' or not stack:
                            stack.append(i)
            else:
                if i + 1 != len(eq):
                    if len(stack) == 1:
                        nxt[stack.pop()] = i + 1
                    else:
                        index = stack.pop()
                        if eq[stack[-1]] in '*/' or eq[i+1] in '+-)':
                            nxt[index] = stack[-1]
                        else:
                            nxt[index] = i + 1
                else:
                    if len(stack) == 1:
                        nxt[stack.pop()] = 0
                    else:
                        while len(stack) != 1:
                            index = stack.pop()
                            nxt[index] = stack[-1]
                        nxt[stack.pop()] = 0
    counter = 1
    nodes = [Node(eq[0], 'Write')]
    generated = {}
    for i in range(1, len(eq)):  # creating nodes array
        if nxt[i] == -1:
            nodes.append(Node(None, None))
        elif eq[i] in '+-*/':
            nodes.append(Node(str(counter), eq[i]))
            counter += 1
        elif eq[i] not in generated:
            generated[eq[i]] = Node(eq[i], 'Read')
            nodes.append(generated[eq[i]])
        else:
            nodes.append(generated[eq[i]])

    graph = {}
    for i in range(2, len(eq)):  # creating graph
        index = nxt[i]
        if index == -1:
            continue
        if not nodes[i] in graph:
            graph[nodes[i]] = [nodes[index]]
        else:
            graph[nodes[i]].append(nodes[index])
        if not nodes[index] in graph:
            graph[nodes[index]] = []

    pred = dfg.find_pred(graph)
    to_change = True
    while to_change:
        to_change = False
        node1 = node2 = None
        for i in graph:
            for j in graph:
                if i == j or not pred[i] or not pred[j]:
                    continue
                if are_same(i, j, pred):
                    to_change = True
                    node1 = i
                    node2 = j
                    break
            if to_change:
                break
        if to_change:
            graph[node1] += graph[node2]
            dfg.remove_node(node2, pred[node2], graph)
            dfg.change_pred(node1, node2, pred)
    return graph


def are_same(node1, node2, pred):
    if node1.func != node2.func:
        return False
    if pred[node1][0].name == pred[node2][0].name and pred[node1][1].name == pred[node2][1].name:
        return True
    if pred[node1][0].name == pred[node2][1].name and pred[node1][1].name == pred[node2][0].name:
        return True


def print_graph(graph):
    for i in graph:
        if graph[i]:
            print(str(i) + " -> " + str(graph[i]))

    for i in graph:
        print(i.name + ": " + i.func)

