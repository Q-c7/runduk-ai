from copy import deepcopy

from picker.app.constants import HEROES
from picker.app.old_python_gui.logic.core import DesktopProgramRunner
from picker.app.old_python_gui.picker_frame.hero_drafter_button import HeroDrafterButton
from picker.app.old_python_gui.stub import AbstractFrame

import tkinter as tk

SLIDER_SIZE = (280, 1080)


class HeroDrafter(AbstractFrame):
    def __init__(self, runner: DesktopProgramRunner, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)

        self.canvas = tk.Canvas(self, width=SLIDER_SIZE[0], height=SLIDER_SIZE[1])
        self.scroll_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.frame = tk.Frame(self.canvas)

        # Line with text
        self.filter_entry = tk.Entry(self)
        self.filter_entry.pack(fill="x")
        self.filter_entry.bind("<KeyRelease>", self.filter_rectangles)
        self.text = ""

        # group of widgets
        self.rectangles: dict[str, HeroDrafterButton] = {}
        all_heroes = deepcopy(HEROES[1:])
        all_heroes.sort(key=lambda h: h.name)
        for hero in all_heroes:
            rect = HeroDrafterButton(master=self.frame, hero=hero, runner=runner)
            rect.pack()  # maybe comment this out
            self.rectangles[hero.name] = rect

        # put the frame in the canvas
        self.canvas.create_window(0, 0, anchor="nw", window=self.frame)
        # make sure everything is displayed before configuring the scrollregion
        self.canvas.update_idletasks()

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all"), yscrollcommand=self.scroll_y.set
        )

        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

        self.canvas.pack(fill="both", expand=True, side="left")
        self.scroll_y.pack(fill="y", side="right")

    def update_ui(self):
        for name, rect in self.rectangles.items():
            if not self.text or name.lower().startswith(self.text.lower()):
                rect.pack()
                rect.set_status(rect.runner.is_in_game(rect.hero.id))
            else:
                rect.pack_forget()

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def filter_rectangles(self, event):
        self.text = self.filter_entry.get()
        self.update_ui()


if __name__ == "__main__":
    root = tk.Tk()
    frame = tk.Frame(root, width=800, height=600)
    frame.pack()
    HeroDrafter(DesktopProgramRunner(), master=frame).pack()
    root.mainloop()
