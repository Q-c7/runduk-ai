import tkinter as tk
from tkinter import ttk

from picker.app.old_python_gui.logic.team import TeamManager
from picker.app.old_python_gui.stub import AbstractFrame
from picker.app.constants import TKINTER_BIG_FONT


class PlayerMenu(AbstractFrame):
    def __init__(self, manager: TeamManager, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.manager = manager

        self.options = self.manager.get_all_players()
        # Create a combo box
        self.combo_box = ttk.Combobox(self, values=self.options, font=TKINTER_BIG_FONT)
        self.combo_box.bind("<<ComboboxSelected>>", self.on_option_selected)
        self.combo_box.current(None)

        self.label = tk.Label(self, text="Choose a player:", font=TKINTER_BIG_FONT)
        self.label.pack()

        # Set up the layout
        self.combo_box.pack()

    def update_ui(self):
        self.options = self.manager.get_all_players()
        self.combo_box.config(values=self.options)

    def on_option_selected(self, event):
        selected_option = self.combo_box.get()
        if selected_option is not None:
            self.manager.set_current_player(selected_option)
