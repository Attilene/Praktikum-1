import os
import tkinter as tk

from config import Configuration as Conf
from frames.game import Game
from frames.overlay import Overlay


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        width = Conf.WIN_WIDTH + Conf.FIELD_BRD_WIDTH
        height = Conf.WIN_HEIGHT + Conf.FIELD_BRD_WIDTH * 2
        if Conf.WITH_ICON:
            icon = tk.PhotoImage(file=Conf.ICON_PATH)
            self.tk.call('wm', 'iconphoto', self._w, icon)
        self.geometry(f"{width}x{height}")
        self.resizable(width=Conf.RESIZABLE, height=Conf.RESIZABLE)
        self.title("TETRIS")
        self.overlay = Overlay(self)
        self.game = Game(self)
        self.counter = self.overlay.counter
        self.next = self.overlay.next
        self.pause = False
        self.interval = self.counter.get_interval()
        self.lines = 0
        self.is_over = False
        self.after_id = ""
        self.bind_id = ""

    def reset(self):
        self.overlay.reset()
        self.game.reset()
        self.pause = False
        self.interval = self.counter.get_interval()
        self.lines = 0
        self.is_over = False
        self.after_cancel(self.after_id)
        self.unbind("<KeyPress>", self.bind_id)

    def key_press(self, event):
        char = event.keysym.lower()
        fld = self.game.field
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
            else:
                print(1)
                self.after_cancel(self.after_id)
                self.process()
        elif char == "p":
            self.pause = not self.pause
        elif char == "r":
            self.reset()

    def start(self):
        """
        Starts after clicking "START".
        """
        self.overlay.button.pack_forget()
        self.next.generate()
        self.game.field.spawn(*self.next.get())
        self.bind_id = self.bind('<KeyPress>', self.key_press)
        self.process()

    def process(self):
        fld = self.game.field
        if not self.is_over:
            self.after_id = self.after(self.interval, self.process)
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
        else:
            self.reset()
