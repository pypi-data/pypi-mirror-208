from bit8 import render, COLORS
from bit8.utils import solid, adjoin, recolor
from bit8.bsl import parse_file

def letter_screen(n):
    b = solid(6, 1, 'n')
    for x in n:
        b = adjoin(b, recolor(LETTERS[x], '# ', 'wn'))
        b = adjoin(b, solid(6, 1, 'n'))
    return b

LETTERS = parse_file('letters.scr')

s = 'the quick brown fox jumps over the lazy dog'
s = 'abcdefghijklmnopqrstuvwxyz'
s += ' ' + ''.join(reversed(s))

for x in s.split():
    render(letter_screen(x))
    print('\n' * 4)
