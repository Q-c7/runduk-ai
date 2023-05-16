import os

from PIL import Image, ImageTk

from picker.app.constants import Hero, TKINTER_BIG_FONT
from picker.app.old_python_gui.logic.team import TeamManager

import tkinter as tk

from picker.app.old_python_gui.stub import AbstractFrame

FRAME_SIZE = (256, 144)


class HeroAdderButton(AbstractFrame):
    def __init__(self, hero: Hero, manager: TeamManager, master=None, *args, **kwargs):
        super().__init__(
            master, *args, **kwargs, width=FRAME_SIZE[0], height=FRAME_SIZE[1]
        )

        self.hero = hero
        self.manager = manager
        self.pos = manager.get_current_pos()

        # Load the image
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(
            script_dir, "../../unfinished_web_gui", "hero_pics", f"{hero.name.lower()}.png"
        )
        assert os.path.exists(image_path), image_path
        image = Image.open(image_path)
        image = image.resize(FRAME_SIZE, Image.LANCZOS)

        self.image = ImageTk.PhotoImage(image)

        # Create a rectangle frame for the button
        self.rectangle_frame = tk.Frame(
            master=self, width=FRAME_SIZE[0], height=FRAME_SIZE[1], bg="blue"
        )  # gray

        # Create a frame for the image
        self.canvas_frame = tk.Frame(
            master=self, width=FRAME_SIZE[0], height=FRAME_SIZE[1]
        )
        canvas = tk.Canvas(
            master=self.canvas_frame, width=FRAME_SIZE[0], height=FRAME_SIZE[1]
        )
        canvas.create_image(0, 0, anchor="nw", image=self.image)
        canvas.pack()

        self.canvas_frame.pack()  # by default image is shown

        # Bind the events for mouse enter and leave
        self.bind("<Enter>", self._show_button)
        self.bind("<Leave>", self._hide_button)

        self.rectangle_frame.propagate(False)
        button = tk.Button(
            self.rectangle_frame,
            text="No player\nselected",
            command=self._button_pressed,
            font=TKINTER_BIG_FONT,
            background="gray",
        )
        button.pack(expand=True, fill=tk.BOTH)

        self.button = button

    def _button_pressed(self):
        player = self.manager.get_current_player()
        if player is None:
            return
        pos = self.manager.get_current_pos()
        is_present = self.hero.id in self.manager.get_player_preferences(player)[pos]
        if is_present:
            self.manager.remove_preference(
                name=player, hero_id=self.hero.id, position=pos
            )
        else:
            self.manager.add_preference(name=player, hero_id=self.hero.id, position=pos)
        # self.update_ui()

    def _show_button(self, event):
        self.canvas_frame.pack_forget()
        self.rectangle_frame.pack()
        # self.update_ui()

    def _hide_button(self, event):
        self.rectangle_frame.pack_forget()
        self.canvas_frame.pack()

    def update_ui(self):
        player = self.manager.get_current_player()
        if player is None:
            self.button.config(text="No player\nselected", background="gray")
            return

        pos = self.manager.get_current_pos()
        is_present = self.hero.id in self.manager.get_player_preferences(player)[pos]
        if is_present:
            self.button.config(
                text=f"Remove {self.hero.name}\nfrom pos {pos}", background="red"
            )
        else:
            self.button.config(
                text=f"Add {self.hero.name}\nto pos {pos}", background="green"
            )


if __name__ == "__main__":
    pass
    # root = tk.Tk()
    # frame = tk.Frame(root, width=800, height=600)
    # frame.pack()
    # runner = DesktopProgramRunner()
    # HeroDrafterButton(HEROES[1], runner, master=frame).pack()
    # root.mainloop()
