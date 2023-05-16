import tkinter as tk

from picker.app.old_python_gui.stub import AbstractFrame
from picker.app.constants import TKINTER_BIG_FONT

PLAYER_WIDGET_SIZE = (300, 300)


class PlayersDisplay(AbstractFrame):
    def __init__(self, manager, master=None, *args, **kwargs):
        super().__init__(
            master=master,
            *args,
            **kwargs,
            width=PLAYER_WIDGET_SIZE[0],
            height=PLAYER_WIDGET_SIZE[1]
        )

        # Line with text
        self.manager = manager
        self.team: list[str] = manager.get_active_players()[:5]

        self.box_frame = tk.Frame(
            self,
            bd=2,
            relief=tk.SOLID,
            width=PLAYER_WIDGET_SIZE[0],
            height=PLAYER_WIDGET_SIZE[1],
        )
        self.box_frame.pack()
        self.update_ui()

    # def add_player(self, player: str) -> None:
    #     if len(self.team) >= 5:
    #         logging.warning("Team is full")
    #         return
    #     self.team.append(player)
    #     # self.update_ui()
    #
    # def remove_player(self, player: str) -> None:
    #     if player not in self.team:
    #         logging.warning("Player not in team")
    #         return
    #     self.team.remove(player)
    # self.update_ui()

    def update_ui(self) -> None:
        self.team = self.manager.get_active_players()[:5]

        self.box_frame.pack_forget()

        self.box_frame = tk.Frame(
            self,
            bd=2,
            relief=tk.SOLID,
            width=PLAYER_WIDGET_SIZE[0],
            height=PLAYER_WIDGET_SIZE[1],
        )
        self.box_frame.pack()

        tk.Label(
            self.box_frame, text="Active players in team:", font=TKINTER_BIG_FONT
        ).pack(side=tk.TOP)

        for player in self.team:
            tk.Label(self.box_frame, text=player, font=TKINTER_BIG_FONT).pack(
                side=tk.TOP
            )
        for _ in range(5 - len(self.team)):
            tk.Label(self.box_frame, text="-", font=TKINTER_BIG_FONT).pack(side=tk.TOP)
