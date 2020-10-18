import tkinter as tk
import time


class Poll(tk.Tk):
    # Settings
    BG = "black"
    START_INTERVAL = 500  # ms
    STICK_LEN = 100  # px (in the start)
    MARGIN = 20  # px
    AUTOZOOM = True
    # Color settings
    COLOR_MODE = "r"  # s = single; g = gradient; r = rainbow
    # Single
    COLOR: str = "purple"  # hex code
    # Gradient
    GRADIENT_GAMMA = 7  # [1; 10]
    GRADIENT_CONTRAST = 5  # [1; 10]
    # Rainbow
    RAINBOW_ORIENTATION = 'c'  # v = vertical; h = horizontal; c = circle; q = square; r = rhombus; re = rhombus elongated; dr = diagonal (up-right angle); dl (up-left angle);
    RAINBOW_RANGE = 1  # [1; 10]
    RAINBOW_COLORS = ["#ff0000", "#ff4e00", "#ffa500", "#ffd200", "#ffff00",
                      "#78bc00", "#008000", "#004478", "#0000ff", "#2600c1",
                      "#4b0082", "#a145bb", "#ee82ee", "#f64279"]
    # Don't touch
    assert 0 <= GRADIENT_GAMMA <= 10, "GRADIENT_GAMMA is out of range"
    assert 0 <= GRADIENT_CONTRAST <= 10, "GRADIENT_CONTRAST is out of range"
    assert 0 <= RAINBOW_RANGE <= 10, "Rainbow_range is out of range"
    GRADIENT_CONTRAST /= 3
    HALF_STICK = STICK_LEN // 2
    RAINBOW_RANGE = (1 / RAINBOW_RANGE) * 2

    def __init__(self, size):
        super().__init__()
        self.wm_title("Practicum of programming")
        self.size = size
        self.center = (size // 2 + 1, size // 2 + 1)
        self.cvs = tk.Canvas(self, width=size, height=size, bg=Poll.BG)
        self.engaged_points = set()
        self.empty_points = {(0, 0)}
        self.out = False
        self.paused = False
        self.zoom = 1
        self.interval = Poll.START_INTERVAL
        self.color = Poll.gradient_color(1) if Poll.COLOR_MODE == "g" else Poll.COLOR
        self.repeat = 1
        self.onstep = 0
        self.amount = 0

        self.cvs.bind("<Button-1>", self.start_pause)

    def start_pause(self, event):
        self.paused = not self.paused

    def to_raw(self, x, y):
        x = self.center[0] + x * self.zoom
        y = self.center[1] - y * self.zoom
        return x, y

    def to_nor(self, x, y):
        x = (x - self.center[0]) / self.zoom
        y = (y - self.center[1]) / -self.zoom
        return x, y

    def get_points(self, x, y):
        orient = self.repeat % 2
        if orient > 0:
            x1 = x - Poll.HALF_STICK
            x2 = x + Poll.HALF_STICK
            y1 = y2 = y
        else:
            y1 = y - Poll.HALF_STICK
            y2 = y + Poll.HALF_STICK
            x1 = x2 = x
        return (x1, y1), (x2, y2)

    def create_stick(self, x, y):
        if (x, y) not in self.engaged_points:
            self.engaged_points.add((x, y))
            p1, p2 = self.get_points(x, y)
            points = {p1, p2}
            total = points & self.empty_points
            for point in total:
                self.empty_points.discard(point)
                self.engaged_points.add(point)
            for point in points - total:
                self.empty_points.add(point)
            self.cvs.create_line(*self.to_raw(*p1), *self.to_raw(*p2), fill=self.color)
            self.onstep += 1
            self.amount += 1
            del (points, total, p1, p2)

    def loop(self):
        if not self.paused:
            for point in set(self.empty_points):
                if Poll.COLOR_MODE == "r":
                    if Poll.RAINBOW_ORIENTATION == 'v':
                        self.color = Poll.rainbow_color(abs(point[0]))
                    elif Poll.RAINBOW_ORIENTATION == 'h':
                        self.color = Poll.rainbow_color(abs(point[1]))
                    elif Poll.RAINBOW_ORIENTATION == 'c':
                        self.color = Poll.rainbow_color((point[0] ** 2 + point[1] ** 2) ** 0.5)
                    elif Poll.RAINBOW_ORIENTATION == 'q':
                        self.color = Poll.rainbow_color(max(map(lambda x: abs(x), point)))
                    elif Poll.RAINBOW_ORIENTATION == 'dr':
                        self.color = Poll.rainbow_color(point[1] - point[0])
                    elif Poll.RAINBOW_ORIENTATION == 'dl':
                        self.color = Poll.rainbow_color(point[1] + point[0])
                    elif Poll.RAINBOW_ORIENTATION == 'r':
                        if point[0] * point[1] > 0:
                            radius = point[1] + point[0]
                        else:
                            radius = point[1] - point[0]
                        self.color = Poll.rainbow_color(radius)
                        del radius
                    elif Poll.RAINBOW_ORIENTATION == 're':
                        if point[0] * point[1] > 0:
                            radius = point[1] / 2 + point[0]
                        else:
                            radius = point[1] / 2 - point[0]
                        self.color = Poll.rainbow_color(radius)
                        del radius
                if not self.out and abs(point[0]) + Poll.HALF_STICK >= self.size / 2 and Poll.AUTOZOOM:
                    self.out = True
                self.empty_points.discard(point)
                self.create_stick(*point)
            if self.out and Poll.AUTOZOOM:
                zoom = (self.size - Poll.MARGIN * 2) / (self.repeat / 2 * Poll.STICK_LEN) / self.zoom
                self.zoom *= zoom
                self.cvs.scale("all", *self.center, zoom, zoom)
                self.interval = round(poll.interval * zoom)
                del zoom
            if Poll.COLOR_MODE == "g":
                self.color = self.gradient_color(self.onstep)
            print(f"{str(self.repeat) + ')':<6} on step: {self.onstep:<7} all: {self.amount}")
            self.repeat += 1
            self.onstep = 0
            del point

        self.after(self.interval, self.loop)

    def start(self):
        self.loop()
        self.cvs.pack()
        self.mainloop()
    
    @staticmethod
    def rainbow_color(radius):
        color = round((radius / Poll.STICK_LEN) * Poll.RAINBOW_RANGE) % len(Poll.RAINBOW_COLORS)
        return Poll.RAINBOW_COLORS[color]
        
    @staticmethod
    def gradient_color(num):
        full_ch = 255
        half_ch = full_ch / 2
        value = (1/num) ** (1/Poll.GRADIENT_GAMMA) * full_ch
        value = value - half_ch
        minus = value < 0
        value = (abs(value) / half_ch) ** (1 / Poll.GRADIENT_CONTRAST) * half_ch
        value = -value if minus else value
        value += half_ch
        value = round(value)
        # Channels
        red = full_ch - value
        green = 100
        blue = value
        return '#%02x%02x%02x' % (red, green, blue)


if __name__ == "__main__":
    poll = Poll(1000)
    poll.start()
