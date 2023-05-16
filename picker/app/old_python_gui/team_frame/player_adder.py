from picker.app.old_python_gui.logic.team import TeamManager

import tkinter as tk

from picker.app.old_python_gui.stub import AbstractFrame
from picker.app.constants import TKINTER_BIG_FONT

PLAYER_ADDER_SIZE = (300, 300)


class PlayerAdder(AbstractFrame):
    def __init__(self, manager: TeamManager, master=None, *args, **kwargs):
        super().__init__(
            master=master,
            *args,
            **kwargs,
            width=PLAYER_ADDER_SIZE[0],
            height=PLAYER_ADDER_SIZE[1],
        )

        self.manager = manager

        self.label = tk.Label(
            self, text="Add new player to database:", font=TKINTER_BIG_FONT
        )
        self.label.pack(expand=True, fill="x")

        # Line with text
        self.filter_entry = tk.Entry(self)
        self.filter_entry.pack(fill="x")
        self.filter_entry.bind("<KeyRelease>", self.redraw_button)
        self.text = ""

        # group of widgets
        self.button = tk.Button(
            self,
            text="Please write new player name",
            font=TKINTER_BIG_FONT,
            command=self._button_pressed,
            background="gray",
        )
        self.button.pack(expand=True, fill=tk.BOTH)

    def _button_pressed(self) -> None:
        text = self.filter_entry.get()
        if self.manager.has_player(text):
            return
        self.manager.add_player(text)
        self.redraw_button(None)

    def update_ui(self) -> None:
        self.redraw_button(None)

    def redraw_button(self, event) -> None:
        text = self.filter_entry.get()
        if not text:
            self.button.config(text="No player\nselected", background="gray")
            return

        if self.manager.has_player(text):
            self.button.config(text=f"Player {text}\nalready exists", background="red")
        else:
            self.button.config(text=f"Add player {text}\nto team", background="green")


# if __name__ == '__main__':
#     root = tk.Tk()
#     frame = tk.Frame(root, width=800, height=600)
#     frame.pack()
#     HeroDrafter(manager=TeamManager(), master=frame).pack()
#     root.mainloop()
