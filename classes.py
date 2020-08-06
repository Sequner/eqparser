class Node:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class PE:
    def __init__(self, name, inputs, wire, operation, is_busy):
        self.name = name             # number of PE
        self.inputs = inputs         # array with size 2
        self.wire = wire             # wire in grid
        self.operation = operation
        self.is_busy = is_busy       # is processing

    def __str__(self):
        return str(self.wire.is_busy)

    def __repr__(self):
        return str(self.wire.is_busy)

class Wire:
    def __init__(self, name, is_busy):
        self.name = name
        self.mode = ""  # not necessary yet
        self.is_busy = is_busy

    def __str__(self):
        return "Wire" + self.name

    def __repr__(self):
        return "Wire" + self.name

class Step:
    def __init__(self, PEs, node_pos):
        self.PEs = PEs
        self.positions = node_pos