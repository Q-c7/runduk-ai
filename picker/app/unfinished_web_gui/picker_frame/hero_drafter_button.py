import os

from PIL import Image

from picker.app.constants import Hero, HEROES
from picker.app.unfinished_web_gui.logic.core import WebProgramRunner

import PySimpleGUIWeb as sg


FRAME_SIZE = (256, 144)


class HeroDrafterButton(sg.Frame):
    def __init__(self, hero: Hero, runner: WebProgramRunner, *args, **kwargs):
        super().__init__(title=f"{hero.name}", layout=[[]], *args, **kwargs)

        self.hero = hero
        self.runner = runner

        # Load the image
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(
            script_dir, "..", "hero_pics", f"{hero.name.lower()}.png"
        )
        assert os.path.exists(image_path), image_path
        image = Image.open(image_path)
        self.image = image.resize(FRAME_SIZE, Image.LANCZOS)

        # Create a frame for the image
        self.canvas_frame = sg.Frame(
            title="",
            layout=[
                [sg.Image(data=self.image)],
            ],
        )

        # Create the buttons with their respective text and colors, attach them to the rectangle frame
        self.buttons = []
        texts = [f"Add \n{hero.name}\n to ", "Ban "]
        teams = ["team", "enemy"]
        colors = ["#80FF80", "#FF8080", "green", "red"]

        for idx, color in enumerate(colors):
            button = sg.Button(
                texts[idx // 2] + teams[idx % 2],
                button_color=("white", color),
                font=("Helvetica", 12),
                size=(10, 3),
                key=f"{hero.name}-{idx}",
            )
            self.buttons.append(button)

        self.layout = [
            [self.canvas_frame],
            [
                sg.Column(
                    layout=[[button]],
                    # justification='center',
                    element_justification="center",
                )
                for button in self.buttons
            ],
        ]

        # self.bind("<Enter>", '_show_buttons')
        # self.bind("<Leave>", '_hide_buttons')

        # self.set_status(False)

    def _button_pressed(self, button_id: int):
        if self.disabled:
            return
        is_enemy = bool(button_id % 2)
        is_ban = bool(button_id // 2)
        self.runner.add_hero(hero_id=self.hero.id, is_enemy=is_enemy, is_ban=is_ban)

    # def _show_buttons(self, event):
    #     self.canvas_frame.Visible = False
    #
    # def _hide_buttons(self, event):
    #     self.canvas_frame.Visible = True
    #
    # def set_status(self, status):
    #     self.disabled = status
    #     for button in self.buttons:
    #         button.update(disabled=status)


if __name__ == "__main__":
    runner = WebProgramRunner()
    layout = [
        [HeroDrafterButton(hero, runner) for hero in HEROES[1:3]],
    ]
    window = sg.Window(
        "Hero Drafter", layout=layout, web_port=8080, web_start_browser=False
    )

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

    window.close()
