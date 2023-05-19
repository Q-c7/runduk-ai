import tkinter as tk

from picker.app.constants import HEROES
from picker.app.old_python_gui.logic.team import TeamManager
from picker.app.old_python_gui.stub import AbstractFrame
from picker.app.constants import TKINTER_BIG_FONT

PLAYER_WIDGET_SIZE = (800, 600)


class TeamHeroesDisplay(AbstractFrame):
    def __init__(self, manager: TeamManager, master=None, *args, **kwargs):
        super().__init__(
            master=master,
            *args,
            **kwargs,
            width=PLAYER_WIDGET_SIZE[0],
            height=PLAYER_WIDGET_SIZE[1],
        )

        self.manager = manager

        self.label = tk.Label(self, text="", font=TKINTER_BIG_FONT)
        # Line with text
        self.heroes: list[list[int]] = [[], [], [], [], []]

        self.box_frame = tk.Frame(
            self,
            bd=2,
            relief=tk.SOLID,
            width=PLAYER_WIDGET_SIZE[0],
            height=PLAYER_WIDGET_SIZE[1],
        )
        self.box_frame.pack()
        self.update_ui()

    def _update_heroes(self) -> str | None:
        current_player = self.manager.get_current_player()
        if current_player is None:
            preferences = self.manager.get_all_preferences()
        else:
            preferences = self.manager.get_player_preferences(current_player)

        self.heroes = [preferences[i] for i in range(1, 6)]

        return current_player

    def update_ui(self) -> None:
        current_player = self._update_heroes()

        self.box_frame.pack_forget()
        self.label.pack_forget()

        text = (
            f"Heroes pool of {current_player}:"
            if current_player
            else "Team heroes pool:"
        )
        self.label = tk.Label(self, text=text, font=TKINTER_BIG_FONT)
        self.label.pack()

        self.box_frame = tk.Frame(
            self,
            bd=2,
            relief=tk.SOLID,
            width=PLAYER_WIDGET_SIZE[0],
            height=PLAYER_WIDGET_SIZE[1],
        )
        self.box_frame.pack()

        for pos, sublist in enumerate(self.heroes):
            list_frame = tk.Frame(self.box_frame)
            list_frame.pack(side=tk.LEFT)

            tk.Label(
                list_frame, text=f"Position {pos+1}:", font=(*TKINTER_BIG_FONT, "bold")
            ).pack(side=tk.TOP)
            # Add labels for each name in the list
            for hero_id in sublist:
                tk.Label(
                    list_frame, text=f"{HEROES[hero_id].name}", font=TKINTER_BIG_FONT
                ).pack(side=tk.TOP)
