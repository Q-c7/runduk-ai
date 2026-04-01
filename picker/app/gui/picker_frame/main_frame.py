import tkinter as tk

from picker.app.gui.logic.core import DesktopProgramRunner
from picker.app.gui.picker_frame.exploration_slider import ExplorationSlider
from picker.app.gui.picker_frame.hero_drafter import HeroDrafter
from picker.app.gui.picker_frame.heroes_container import HeroesContainer
from picker.app.gui.picker_frame.prediction_display import PredictionDisplay
from picker.app.gui.picker_frame.rank_menu import RankMenu
from picker.app.constants import TKINTER_SMALL_FONT


class PickerFrame(tk.Frame):
    def __init__(self, master=None, model_path="latest"):
        super().__init__(master=master)
        self.configure(width=1800, height=700)
        # TODO: refactor this code later
        self.runner = DesktopProgramRunner(model_path=model_path)

        # Create slider
        self.slider = HeroDrafter(master=self, runner=self.runner)
        self.slider.config(width=300)
        self.runner.add_ui_element(self.slider)

        # Set up main frames
        self.grid_frame = tk.Frame(self)
        self.predictor_frame = tk.Frame(self)

        # Create HeroesContainer instances and add them to runner
        self.my_heroes = HeroesContainer(
            master=self.grid_frame, runner=self.runner, is_enemy=False, is_ban=False
        )
        self.enemy_heroes = HeroesContainer(
            master=self.grid_frame, runner=self.runner, is_enemy=True, is_ban=False
        )
        self.my_bans = HeroesContainer(
            master=self.grid_frame, runner=self.runner, is_enemy=False, is_ban=True
        )
        self.enemy_bans = HeroesContainer(
            master=self.grid_frame, runner=self.runner, is_enemy=True, is_ban=True
        )
        self.runner.add_ui_element(self.my_heroes)
        self.runner.add_ui_element(self.enemy_heroes)
        self.runner.add_ui_element(self.my_bans)
        self.runner.add_ui_element(self.enemy_bans)

        # Create rank menu and swap teams button
        swap_teams_button = tk.Button(
            self.grid_frame, text="Swap teams and bans", command=self.runner.swap_teams
        )
        rank_button = RankMenu(master=self.grid_frame, runner=self.runner)

        # Create PredictionDisplay
        predictor_widget = PredictionDisplay(master=self.predictor_frame)
        self.runner.set_prediction_display(predictor_widget)

        # Create a container for the right-side controls
        controls_frame = tk.Frame(self.predictor_frame)

        # Create ExplorationSlider
        exploration_slider = ExplorationSlider(
            master=controls_frame, predictor_widget=predictor_widget
        )

        app = getattr(getattr(self.master, "master", None), "show_frame", None)
        if app is not None:
            go_back_button = tk.Button(
                controls_frame,
                text="← Back to Team",
                command=lambda: app("TeamFrame"),
                font=TKINTER_SMALL_FONT,
            )

            # Stack the controls vertically
            exploration_slider.pack(side="top", pady=(0, 5))
            go_back_button.pack(side="top")

        # Pack the grid into grid frame
        self.my_heroes.grid(row=0, column=0, padx=10, pady=50)
        swap_teams_button.grid(row=0, column=1, padx=10, pady=50)
        self.enemy_heroes.grid(row=0, column=2, padx=10, pady=50)
        self.my_bans.grid(row=1, column=0, padx=10, pady=50)
        rank_button.grid(row=1, column=1, padx=10, pady=50)
        self.enemy_bans.grid(row=1, column=2, padx=10, pady=50)

        # Pack everything into predictor frame - give more space to predictions
        predictor_widget.pack(side="left", fill="both", expand=True)
        controls_frame.pack(side="right", padx=(10, 0))

        # Show everything: slider on the left, then grid on the top and predictor on the bottom
        self.slider.pack(side="left", padx=10, pady=10)
        self.grid_frame.pack(side="top")
        self.predictor_frame.pack(side="bottom")


if __name__ == "__main__":
    root = tk.Tk()

    frame = PickerFrame()
    frame.pack()

    root.mainloop()
