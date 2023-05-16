import tkinter as tk

from picker.app.old_python_gui.logic.team import TeamManager
from picker.app.old_python_gui.team_frame.hero_adder import HeroAdder
from picker.app.old_python_gui.team_frame.player_adder import PlayerAdder
from picker.app.old_python_gui.team_frame.player_menu import PlayerMenu
from picker.app.old_python_gui.team_frame.players_display import PlayersDisplay
from picker.app.old_python_gui.team_frame.position_menu import PositionMenu
from picker.app.old_python_gui.team_frame.team_controls import TeamControls
from picker.app.old_python_gui.team_frame.team_heroes_display import TeamHeroesDisplay


class TeamFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.configure(width=1400, height=700)
        # TODO: refactor this code later
        self.manager = TeamManager()

        # Create slider
        self.slider = HeroAdder(master=self, manager=self.manager)
        self.slider.config(width=300)
        self.manager.add_ui_element(name="hero_adder", element=self.slider)

        # Set up main frames
        self.grid_frame = tk.Frame(self)
        self.bottom_frame = tk.Frame(self)

        # grid frame: top row
        self.player_adder = PlayerAdder(master=self.grid_frame, manager=self.manager)
        self.players_display = PlayersDisplay(
            master=self.grid_frame, manager=self.manager
        )

        # grid frame: bottom row
        self.team_controls = TeamControls(master=self.grid_frame, manager=self.manager)
        self.position_menu = PositionMenu(master=self.grid_frame, manager=self.manager)
        self.player_menu = PlayerMenu(master=self.grid_frame, manager=self.manager)

        self.manager.add_ui_element(name="player_adder", element=self.player_adder)
        self.manager.add_ui_element(name="team_controls", element=self.team_controls)
        self.manager.add_ui_element(
            name="players_display", element=self.players_display
        )
        self.manager.add_ui_element(name="player_menu", element=self.player_menu)

        # bottom frame
        self.team_heroes_display = TeamHeroesDisplay(
            master=self.bottom_frame, manager=self.manager
        )
        self.manager.add_ui_element(
            name="team_heroes_display", element=self.team_heroes_display
        )

        # fixme come up with an interface of some sort
        if hasattr(self.master, "master") and hasattr(self.master.master, "show_frame"):
            go_back_button = tk.Button(
                self.bottom_frame,
                text="Save and go to picker screen",
                command=self._next_stage,
            )

            go_back_button.pack(side="left")

        # Pack the grid into grid frame
        self.player_adder.grid(row=0, column=0, padx=10, pady=50)
        self.players_display.grid(row=0, column=1, padx=10, pady=50)

        self.team_controls.grid(row=1, column=0, padx=10, pady=50)
        self.position_menu.grid(row=1, column=1, padx=10, pady=50)
        self.player_menu.grid(row=1, column=2, padx=10, pady=50)

        # Pack everything left into predictor frame
        self.team_heroes_display.pack(side="left")

        # Show everything: slider on the left, then grid on the top and predictor on the bottom
        self.slider.pack(side="left", padx=10, pady=10)
        self.grid_frame.pack(side="top")
        self.bottom_frame.pack(side="bottom")

    def _next_stage(self):
        assert hasattr(self.master, "master") and hasattr(
            self.master.master, "show_frame"
        )
        self.manager.save_team()

        self.master.master.show_frame(
            "PickerFrame", to_predictor=self.manager.get_reversed_preferences()
        )


if __name__ == "__main__":
    root = tk.Tk()

    frame = TeamFrame()
    frame.pack()

    root.mainloop()
