import keyboard as kb
from prx import *
from time import sleep

def bound(x, v, y):
    if v < x: return x
    if v > y: return y
    return v

HEIGHT, WIDTH = 100, 100

r = Renderer()
s = Screen(HEIGHT, WIDTH)

x, y = 0, 0
while True:
    if kb.is_pressed('w'): y = bound(0, y - 1, HEIGHT - 1)
    if kb.is_pressed('a'): x = bound(0, x - 1, WIDTH - 1)
    if kb.is_pressed('s'): y = bound(0, y + 1, HEIGHT - 1)
    if kb.is_pressed('d'): x = bound(0, x + 1, WIDTH - 1)
    s.wipe()
    s.pixels[y][x] = 'r'
    r.render(s)
    # print(y, x)
    sleep(0.01)
