import tkinter as tk

from config import Configuration as Conf
from field import Field


class Game(tk.Canvas):
    def __init__(self, window):
        super().__init__(master=window,
                         width=Conf.WIN_WIDTH - Conf.OVERLAY_WIDTH + Conf.FIELD_BRD_WIDTH,
                         height=Conf.WIN_HEIGHT + Conf.FIELD_BRD_WIDTH * 2,
                         bg=Conf.BG_CLR,
                         highlightthickness=0)
        self.pack_propagate(False)
        self.pack(side=tk.LEFT)
        self.field = Field(self)
        self.counter = self.master.overlay.counter
        self.next = self.master.overlay.next
        self.pause = False
        self.interval = self.counter.get_interval()
        self.lines = 0
        self.is_over = False

    def key_press(self, event):
        char = event.keysym.lower()
        fld = self.field
        if char == 'left':
            if fld.can_move(-1, 0):
                fld.left()
        elif char == 'right':
            if fld.can_move(1, 0):
                fld.right()
        elif char == 'up':
            if fld.can_rotate():
                fld.rotate()
        elif char == 'down':
            if fld.can_move():
                fld.step()
        elif char == "p":
            self.pause = not self.pause
        elif char == "r":
            self.reset()

    def start(self):
        """
        Starts after clicking "START".
        """
        self.master.overlay.start.pack_forget()
        self.next.generate()
        self.field.spawn(*self.next.get())
        self.master.bind('<KeyPress>', self.key_press)
        self.process()

    def process(self):
        fld = self.field
        if not self.is_over:
            self.master.after(self.interval, self.process)
            if not self.pause:
                if fld.can_move():
                    fld.step()
                else:
                    fld.fall()
                    new_lines = fld.clear_full()
                    self.counter.raise_score(Conf.POINTS_FOR_LINES[new_lines])
                    self.lines += new_lines
                    if self.lines >= Conf.LEVEL_CONDITION:
                        self.lines -= Conf.LEVEL_CONDITION
                        self.counter.raise_level()
                        self.interval = self.counter.get_interval()
                    self.is_over = fld.is_lose()
                    if not self.is_over:
                        fld.spawn(*self.next.get())
                        self.next.generate()
