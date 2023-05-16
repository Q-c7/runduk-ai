import os

from PIL import Image, ImageTk

from picker.app.constants import Hero, HEROES
from picker.app.old_python_gui.logic.core import DesktopProgramRunner

import tkinter as tk


FRAME_SIZE = (256, 144)
# FRAME_SIZE = (20, 16)


class HeroDrafterButton(tk.Frame):
    def __init__(
        self, hero: Hero, runner: DesktopProgramRunner, master=None, *args, **kwargs
    ):
        super().__init__(
            master, *args, **kwargs, width=FRAME_SIZE[0], height=FRAME_SIZE[1]
        )

        self.hero = hero
        self.runner = runner

        # Load the image
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(
            script_dir, "../../unfinished_web_gui", "hero_pics", f"{hero.name.lower()}.png"
        )
        assert os.path.exists(image_path), image_path
        image = Image.open(image_path)
        image = image.resize(FRAME_SIZE, Image.LANCZOS)

        self.image = ImageTk.PhotoImage(image)

        # Create a rectangle frame for the buttons
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
        self.bind("<Enter>", self._show_buttons)
        self.bind("<Leave>", self._hide_buttons)

        # Create the buttons with their respective text and colors, attach them to the rectangle frame
        self.buttons = []
        texts = [f"Add \n{hero.name}\n to ", "Ban "]
        teams = ["team", "enemy"]
        colors = ["#80FF80", "#FF8080", "green", "red"]

        for idx, color in enumerate(colors):
            button_frame = tk.Frame(
                self.rectangle_frame,
                width=FRAME_SIZE[0] // 2,
                height=FRAME_SIZE[1] // 2,
            )
            button_frame.propagate(False)

            button = tk.Button(
                button_frame,
                text=texts[idx // 2] + teams[idx % 2],
                command=lambda button_id=idx: self._button_pressed(button_id),
                background=color,
            )
            button.pack(expand=True, fill=tk.BOTH)
            # width=FRAME_SIZE[0] // 20,
            # height=FRAME_SIZE[1] // 40)
            # button.config(width=FRAME_SIZE[0] // 2, height= FRAME_SIZE[1] // 2)
            # button.place(x=(idx % 2) * 128,
            #              y=(idx // 2) * 72,
            #              width=FRAME_SIZE[0] // 2,
            #              height= FRAME_SIZE[1] // 2)
            button_frame.grid(row=(idx % 2), column=(idx // 2), padx=0, pady=0)
            self.buttons.append(button_frame)

        # Dark rectangle which is drawn when hero is already picked / banned
        self.overlay = tk.Canvas(self)
        self.overlay.place(x=0, y=0, width=256, height=144)
        self.overlay.create_rectangle(
            0, 0, 256, 144, fill="black", stipple="gray50", tags="overlay"
        )
        self.overlay.lower("overlay")
        self.overlay.place_forget()
        # TODO: https://stackoverflow.com/questions/54637795/how-to-make-a-tkinter-canvas-rectangle-transparent
        self.disabled = False

    def _button_pressed(self, button_id: int):
        if self.disabled:
            return
        is_enemy = bool(button_id % 2)
        is_ban = bool(button_id // 2)
        self.runner.add_hero(hero_id=self.hero.id, is_enemy=is_enemy, is_ban=is_ban)

    def _show_buttons(self, event):
        # for idx, button_frame in enumerate(self.buttons):
        #     button_frame.grid(row=(idx % 2), column=(idx // 2))
        #     button_frame.tkraise()
        self.canvas_frame.pack_forget()
        self.rectangle_frame.pack()

    def _hide_buttons(self, event):
        # for button_frame in self.buttons:
        #     button_frame.grid_forget()
        self.rectangle_frame.pack_forget()
        self.canvas_frame.pack()

    def set_status(self, status):
        self.disabled = status
        if status:
            self.overlay.place(x=0, y=0)
        else:
            self.overlay.place_forget()


if __name__ == "__main__":
    root = tk.Tk()
    frame = tk.Frame(root, width=800, height=600)
    frame.pack()
    runner = DesktopProgramRunner()
    HeroDrafterButton(HEROES[1], runner, master=frame).pack()
    root.mainloop()
