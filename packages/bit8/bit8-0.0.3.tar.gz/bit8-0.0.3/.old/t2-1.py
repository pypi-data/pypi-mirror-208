from bit8 import *

s1 = screen_from_filename('s1.scr')
s2 = screen_from_filename('s2.scr')

from time import sleep

while True:
    render(s1)
    sleep(1)
    render(s2)
    sleep(1)
