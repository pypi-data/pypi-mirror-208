import atexit
import sys
import io

COLORS = 'nrgybpcw'
CURSOR_VISIBILITY = True

class ansi:
    up = staticmethod(lambda x: print(end=f'\033[{x}A'))
    down = staticmethod(lambda x: print(end=f'\033[{x}B'))
    right = staticmethod(lambda x: print(end=f'\033[{x}C'))
    left = staticmethod(lambda x: print(end=f'\033[{x}D'))
    reset = staticmethod(lambda: print(end='\033[0m'))
    background_color_codes = dict(zip(COLORS, range(40, 48)))    # n: "noir", c: cyan
    foreground_color_codes = dict(zip(COLORS, range(30, 38)))

    @staticmethod
    def set_colors(fg=None, bg=None):
        fgl = ansi.foreground_color_codes.get(fg)
        bgl = ansi.background_color_codes.get(bg)
        if fg == ' ': fgl = '30'  # need to make it transparent
        if bg == ' ': bgl = '30'
        if type(fg) is tuple: print(end='\033[38;2;' + ';'.join(map(str, fg)) + 'm')
        elif fgl: print(end=f'\033[{fgl}m')
        if type(bg) is tuple: print(end='\033[48;2;' + ';'.join(map(str, bg)) + 'm')
        elif bgl: print(end=f'\033[{bgl}m')

    @staticmethod
    def move_cursor(current_location, new_location):
        delta = [new_location[0] - current_location[0], new_location[1] - current_location[1] - 1]
        if delta[0] < 0: ansi.up(abs(delta[0]))
        else: ansi.down(delta[0])
        if delta[1] < 0: ansi.left(abs(delta[1]))
        else: ansi.right(delta[1])
        current_location = new_location

    @staticmethod
    def show_cursor():
        global CURSOR_VISIBILITY
        CURSOR_VISIBILITY = True
        print(end='\x1b[?25h')

    @staticmethod
    def hide_cursor():
        global CURSOR_VISIBILITY
        CURSOR_VISIBILITY = False
        print(end='\x1b[?25l')

atexit.register(ansi.show_cursor)
atexit.register(ansi.reset)

cursor = [0, 0]

def render(scr, move_cursor=True):
    if move_cursor:
        if CURSOR_VISIBILITY:
            ansi.hide_cursor()
        global cursor
        ansi.move_cursor(cursor, [0, 0])
        cursor = [0, 0]
    pixels = scr.copy()
    if len(pixels) % 2 == 1: pixels.append(['n'] * len(scr[0]))
    raw_pixels = list(zip(*[iter(pixels)] * 2))
    for x, y in raw_pixels:
        for bg, fg in zip(x, y):
            ansi.set_colors(fg, bg)
            print(end='▄')
        print()
        if move_cursor: cursor[0] += 1

def as_str(scr):
    sys.stdout = io.StringIO()
    render(scr, move_cursor=False)
    s = sys.stdout.getvalue()
    sys.stdout = sys.__stdout__
    return s

def screen_from_str(s):
    return [[x.lower() if x != ' ' else 'n' for x in y] for y in s.strip().split('\n')]

def screen_from_filename(fn):
    with open(fn) as f: return screen_from_str(f.read())
