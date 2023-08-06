from itertools import zip_longest

class ansi:
    up = staticmethod(lambda x: print(end=f'\033[{x}A'))
    down = staticmethod(lambda x: print(end=f'\033[{x}B'))
    right = staticmethod(lambda x: print(end=f'\033[{x}C'))
    left = staticmethod(lambda x: print(end=f'\033[{x}D'))
    background_color_codes = dict(zip('nrgybpcw', range(40, 48)))    # n: "noir", c: cyan
    foreground_color_codes = dict(zip('nrgybpcw', range(30, 38)))

    @staticmethod
    def set_colors(fg=None, bg=None):
        fgl = ansi.foreground_color_codes.get(fg)
        bgl = ansi.background_color_codes.get(bg)
        if fg == ' ': fgl = '0'
        if bg == ' ': bgl = '0'
        if fgl: print(end=f'\033[{fgl}m')
        if bgl: print(end=f'\033[{bgl}m')

class Screen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.wipe()

    def wipe(self):
        self.pixels = [['n' for _ in range(self.width)] for _ in range(self.height)]

    @property
    def _raw_pixels(self):
        pixels = self.pixels.copy()
        if len(pixels) % 2 == 1: pixels.append(['n'] * self.width)
        return list(zip_longest(*[iter(pixels)] * 2))

    @staticmethod
    def from_file(filename):
        with open(filename) as f: s = f.read()
        scr = Screen(s.index('\n'), s.count('\n') + 1)
        scr.pixels = [[x.lower() if x != ' ' else 'n' for x in y] for y in s.strip().split('\n')]
        return scr

    def render(self):
        for x, y in self._raw_pixels:
            for bg, fg in zip(x, y):
                ansi.set_colors(fg, bg)
                print(end='▄')
            print()

class Renderer:
    def __init__(self):
        self.cursor = [0, 0]

    def move_cursor(self, new_location):
        delta = [new_location[0] - self.cursor[0], new_location[1] - self.cursor[1] - 1]
        if delta[0] < 0: ansi.up(abs(delta[0]))
        else: ansi.down(delta[0])
        if delta[1] < 0: ansi.left(abs(delta[1]))
        else: ansi.right(delta[1])
        self.cursor = new_location

    def render(self, screen):
        self.move_cursor([0, 0])
        screen.render()
        self.cursor = [len(screen._raw_pixels), 0]   # Make faster

def main():
    s1 = Screen.from_file('s1.scr')
    s2 = Screen.from_file('s2.scr')

    from time import sleep
    r = Renderer()
    while True:
        r.render(s1)
        sleep(1)
        r.render(s2)
        sleep(1)

if __name__ == '__main__': main()
