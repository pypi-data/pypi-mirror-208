# Black and white (with higher resolution)

import itertools as it
import operator as op
from .bit8 import ansi
import sys
import io

class ForgivingList(list):
    def __init__(self, l, default):
        super().__init__(l)
        self.default = default
    def __getitem__(self, k):
        try:
            r = list.__getitem__(self, k)
            if type(r) is list:
                return ForgivingList(r, self.default.default)   # Not general purpose
            return r
        except IndexError:
            return self.default

def ipad(scr):
    for x in scr:
        if len(x) % 2 != 0:
            x.append(0)
    if len(scr) % 4 != 0:
        for _ in range(len(scr) % 4):
            scr.append([0] * len(scr[0]))

def screen_to_units(_scr):
    xsize = 2
    ysize = 4
    scr = ForgivingList(_scr, ForgivingList([], default=0))
    # Pray forgive this monstrosity, O God, for the pains of pragmatricity needle me far more so than
    # that lofty ideal of mathematical purity, held for too long in its ivory tower. Shine your light
    # on one who is undeserving, this man to whom hope has fled like the wisdom of his ancestors long
    # passed. ILLUMINATE this code for it is wretched, and REDEEM it so that its worthiness to an eye
    # held by the masters of yore may be filled with many a tear, and not in sorrow.
                                                                                 #   signed, the unawakened coder
    return [[[[scr[ys + y][xs + x] for x in range(xsize)] for y in range(ysize)] for xs in range(0, len(scr[0]), xsize)] for ys in range(0, len(scr), ysize)]

def unit_to_braille(unit):
    l = list(map(op.itemgetter(1), sorted(zip([1,2,3,7,4,5,6,8], it.chain.from_iterable(zip(*unit))))))
    v = sum(map(op.mul, l, map(pow, it.repeat(2), it.count())))
    return chr(v + 10240)

def render(scr, move_cursor=True):
    ipad(scr)
    l = screen_to_units(scr)
    for y in l:
        for x in y:
            print(unit_to_braille(x), end='')
        print()
    if move_cursor:
        ansi.up(len(l))

def as_str(scr):
    sys.stdout = io.StringIO()
    render(scr, move_cursor=False)
    s = sys.stdout.getvalue()
    sys.stdout = sys.__stdout__
    return s
