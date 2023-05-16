from picker.app.old_python_gui.logic.team import TeamManager

import tkinter as tk

from picker.app.old_python_gui.stub import AbstractFrame
from picker.app.constants import TKINTER_BIG_FONT

TEAM_CONROLS_SIZE = (500, 500)


class TeamControls(AbstractFrame):
    def __init__(self, manager: TeamManager, master=None, *args, **kwargs):
        super().__init__(
            master=master,
            *args,
            **kwargs,
            width=TEAM_CONROLS_SIZE[0],
            height=TEAM_CONROLS_SIZE[1],
        )

        self.manager = manager

        # Line with text
        current_player = self.manager.get_current_player() or ""
        self.current_player_label = tk.Label(
            self,
            text=f"Current player: {current_player}",
            font=TKINTER_BIG_FONT,
            background="white",
        )
        self.current_player_label.pack(fill="x", side=tk.TOP)

        # group of widgets
        self.deselect_button = tk.Button(
            self,
            text="Select\nteam",
            command=self._deselect,
            background="blue",
            font=TKINTER_BIG_FONT,
        )
        self.deselect_button.pack(fill="x", side=tk.TOP)

        self.change_status_button = tk.Button(
            self,
            text="Add player\nto team",
            command=self._change_status,
            background="gray",
            font=TKINTER_BIG_FONT,
        )
        self.change_status_button.pack(fill="x", side=tk.TOP)

        self.delete_button = tk.Button(
            self,
            text="DELETE\nPLAYER",
            command=self._delete,
            background="red",
            font=TKINTER_BIG_FONT,
        )
        self.delete_button.pack(fill="x", side=tk.TOP)

    def update_ui(self) -> None:
        current_player = self.manager.get_current_player()
        self.current_player_label.configure(
            text=f"Current player: {current_player}" or "No player selected"
        )
        if current_player is not None and self.manager.is_active(current_player):
            text = "Remove player\nfrom team"
        else:
            text = "Add player\nto team"
        self.change_status_button.configure(text=text)

    def _deselect(self) -> None:
        self.manager.set_current_player(None)

    def _change_status(self) -> None:
        current_player = self.manager.get_current_player()
        if current_player is None:
            return
        self.manager.change_status(current_player)

    def _delete(self) -> None:
        current_player = self.manager.get_current_player()
        if current_player is None:
            return
        self.manager.remove_player(current_player)
