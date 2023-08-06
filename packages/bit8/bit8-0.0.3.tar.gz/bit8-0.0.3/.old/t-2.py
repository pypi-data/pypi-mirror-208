from bit8 import render, screen_from_str
from bit8.utils import overlay, solid
from time import sleep
import keyboard as kb

def bound(x, v, y):
    if v < x: return x
    if y < v: return y
    return v

posx, posy = 3, 5
width, height = 50, 50

board = solid(height, width, 'n')
sprite = solid(2, 2, 'r')

try:
    while True:
        if kb.is_pressed('w'): posy -= 1
        if kb.is_pressed('a'): posx -= 1
        if kb.is_pressed('s'): posy += 1
        if kb.is_pressed('d'): posx += 1
        render(overlay(board, sprite, (posy, posx)))
        sleep(0.05)
except KeyboardInterrupt: pass
