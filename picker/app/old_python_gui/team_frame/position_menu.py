import tkinter as tk
from tkinter import ttk

from picker.app.old_python_gui.logic.team import TeamManager
from picker.app.constants import TKINTER_BIG_FONT


class PositionMenu(tk.Frame):
    def __init__(self, manager: TeamManager, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.manager = manager

        self.options = [
            "Position 1 (Carry)",
            "Position 2 (Midlaner)",
            "Position 3 (Offlaner)",
            "Position 4 (Soft Support)",
            "Position 5 (Hard Support)",
        ]

        # Create a combo box
        self.combo_box = ttk.Combobox(self, values=self.options, font=TKINTER_BIG_FONT)
        self.combo_box.bind("<<ComboboxSelected>>", self.on_option_selected)
        self.combo_box.current(0)

        self.label = tk.Label(self, text="Select a position", font=TKINTER_BIG_FONT)
        self.label.pack()

        # Set up the layout
        self.combo_box.pack()

    def on_option_selected(self, event):
        selected_option = self.combo_box.get()
        for idx, opt in enumerate(self.options):
            if opt == selected_option:
                self.manager.set_current_pos(current_pos=idx + 1)
                break
