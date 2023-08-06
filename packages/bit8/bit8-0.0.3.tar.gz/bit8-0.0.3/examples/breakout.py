#!/mnt/c/WINDOWS/py.exe

from bit8 import render, COLORS
from bit8.utils import overlay, solid, ScreenClass, adjoin, recolor
from bit8.game import overlapping_area
from bit8.bsl import parse_file
from random import choice
from keyboard import is_pressed
from time import sleep
from math import sin, cos, radians

def bound(x, v, y):
    if v < x: return x
    if v > y: return y
    return v

def number_screen(n):
    b = solid(6, 1, 'n')
    for x in str(n):
        b = adjoin(b, recolor(NUMBERS[x], '# ', 'wn'))
        b = adjoin(b, solid(6, 1, 'n'))
    return b

HEIGHT, WIDTH = 50, 50
PADDLE_WIDTH = 4
BALL_SIZE = 2

score = 0

NUMBERS = parse_file('numbers.scr')

board = solid(HEIGHT, WIDTH, 'n')
paddle = solid(1, PADDLE_WIDTH, 'g')
ball = solid(BALL_SIZE, BALL_SIZE, 'r')

paddle_pos = 0
theta, v = 60, 1
ball_pos = [HEIGHT//2, 0]

try:
    while True:
        if is_pressed('k'): paddle_pos = bound(0, paddle_pos - 1, WIDTH - PADDLE_WIDTH)
        if is_pressed('l'): paddle_pos = bound(0, paddle_pos + 1, WIDTH - PADDLE_WIDTH)
        ball_pos[0] += cos(radians(theta)) * v
        ball_pos[1] += sin(radians(theta)) * v

        if not 0 < ball_pos[0] < HEIGHT - BALL_SIZE: theta = 180 - theta
        if not 0 < ball_pos[1] < WIDTH - BALL_SIZE: theta = - theta
        elif overlapping_area((HEIGHT - 5, paddle_pos), (1, PADDLE_WIDTH), ball_pos, (BALL_SIZE, BALL_SIZE)) >= 0:
            theta *= ball_pos[1] - paddle_pos
            score += 1

        render(adjoin(overlay(overlay(board, ball, tuple(map(int, ball_pos))), paddle, (HEIGHT - 5, paddle_pos)), number_screen(score)))
        sleep(0.02)
except KeyboardInterrupt:
    pass
