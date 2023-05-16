import tkinter as tk
from tkinter import ttk

from picker.app.old_python_gui.logic.core import DesktopProgramRunner


class RankMenu(tk.Frame):
    def __init__(self, runner: DesktopProgramRunner, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.runner = runner

        self.options = [
            "Herald",
            "Guardian",
            "Crusader",
            "Archon",
            "Legend",
            "Ancient+",
        ]

        # Create a combo box
        self.combo_box = ttk.Combobox(self, values=self.options)
        self.combo_box.bind("<<ComboboxSelected>>", self.on_option_selected)
        self.combo_box.current(0)

        # Set up the layout
        self.combo_box.pack()

    def on_option_selected(self, event):
        selected_option = self.combo_box.get()
        for idx, opt in enumerate(self.options):
            if opt == selected_option:
                self.runner.change_rank(new_rank=idx)
                break
