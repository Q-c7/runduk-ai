import logging
import os

from picker.app.constants import HEROES
from picker.app.old_python_gui.logic.core import DesktopProgramRunner
from picker.app.old_python_gui.stub import AbstractFrame

import tkinter as tk
from PIL import ImageTk, Image


def _get_transparent_image(scale):
    return ImageTk.PhotoImage(Image.new("RGBA", scale, (0, 0, 0, 0)))


class HeroesContainer(AbstractFrame):
    def __init__(self, runner, is_enemy, is_ban, master=None, *args, **kwargs):
        self.scale = (64, 36) if is_ban else (128, 72)
        self.button_count = (4, 3) if is_ban else (3, 2)

        self.width = self.scale[0] * self.button_count[0]
        self.height = self.scale[1] * 2 + 4

        super().__init__(master, *args, **kwargs, width=self.width, height=self.height)
        self.buttons = []
        self.is_enemy = is_enemy
        self.runner = runner
        self.is_ban = is_ban

        # Create main frame for buttons
        # self.grid_frame = tk.Frame(self)
        # self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Create buttons with images and internal IDs
        for idx in range(sum(self.button_count)):
            # button_frame = tk.Frame(self.grid_frame, width=self.scale[0], height=self.scale[1])

            button = tk.Button(
                self,
                command=lambda button_id=idx: self.button_clicked(button_id),
                width=self.scale[0],
                height=self.scale[1],
                borderwidth=1,
                relief=tk.GROOVE,
            )
            button.config(image=_get_transparent_image(self.scale))
            button.image = _get_transparent_image(self.scale)

            x = (idx % self.button_count[0]) * self.scale[0] + (
                idx >= self.button_count[0]
            ) * (self.scale[0] // 2)
            y = (idx // self.button_count[0]) * (self.scale[1] + 4)
            button.place(x=x, y=y)
            # button_frame.button_obj = button
            self.buttons.append(button)

        self.update_ui()

    @staticmethod
    def _get_image(hero, scale):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(
            script_dir,
            "../../unfinished_web_gui",
            "hero_pics",
            f"{hero.name.lower()}.png",
        )
        assert os.path.exists(image_path), image_path
        image = Image.open(image_path)
        image = image.resize(scale, Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def update_ui(self):
        team = self.runner.container(is_enemy=self.is_enemy, is_ban=self.is_ban)

        for hero_id, button in zip(team, self.buttons):
            assert len(HEROES) > hero_id > 0
            button.image = self._get_image(HEROES[hero_id], scale=self.scale)
            button.configure(image=button.image)

        for button in self.buttons[len(team) :]:
            button.image = _get_transparent_image(self.scale)
            button.config(image=button.image)

    def button_clicked(self, button_id: int):
        team = self.runner.container(is_enemy=self.is_enemy, is_ban=self.is_ban)
        if button_id >= len(team):
            logging.info("Most likely user tried to remove an empty hero, skipping...")
            return
        removed_hero_id = team[button_id]
        self.runner.remove_hero(
            hero_id=removed_hero_id, is_enemy=self.is_enemy, is_ban=self.is_ban
        )


if __name__ == "__main__":
    root = tk.Tk()
    runner = DesktopProgramRunner()
    runner._my_team = [10, 11, 12, 13, 14]
    elem = HeroesContainer(runner=runner, is_enemy=False, is_ban=False)
    runner.add_ui_element(elem)
    elem.pack()
    root.mainloop()
