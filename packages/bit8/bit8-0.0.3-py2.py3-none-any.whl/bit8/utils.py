from copy import deepcopy

class ScreenClass(list):   # Fix
    def __init__(self, v):
        self.v = v
    def __getitem__(self, i): return self.v[i]
    def overlay(*args): return ScreenClass(overlay(*args))
    def recolor(*args): return ScreenClass(recolor(*args))
    def adjoin(*args): return ScreenClass(adjoin(*args))

def overlay(scr1, scr2, location=(0, 0)):   # Probably could optimize with laziness
    ret = deepcopy(scr1)
    by, bx = len(ret), len(ret[0])
    for y in range(location[0], location[0] + len(scr2)):
        for x in range(location[1], location[1] + len(scr2[0])):
            if 0 <= x < bx and 0 <= y < by:
                ret[y][x] = scr2[y - location[0]][x - location[1]]
    return ret

def solid(height, width, color):
    return [[color for _ in range(width)] for _ in range(height)]   # No faster way to do this?

def recolor(scr, c1, c2):
    lk = dict(zip(c1, c2))
    return [[lk.get(x, x) for x in y] for y in scr]  # Really have to improve performance

def transpose(scr):
    return list(zip(*scr))

def adjoin(scr1, scr2, direction='horizontal', buffer=0):
    s1 = deepcopy(scr1)
    if direction == 'horizontal':
        for i, row in enumerate(scr2):
            s1[i] += list('n' * buffer) + row
        return s1
    elif direction == 'vertial':
        return transpose(adjoin(transpose(scr1), transpose(scr2)))   # IDK if this works
