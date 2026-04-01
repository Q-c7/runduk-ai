import os

from PIL import Image, ImageDraw, ImageFont, ImageTk

from picker.app.constants import Hero, HEROES
from picker.app.gui.logic.core import DesktopProgramRunner

import tkinter as tk


FRAME_SIZE = (256, 144)

HERO_PICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hero_pics")


def _make_placeholder(name: str) -> Image.Image:
    """Generate a colored rectangle with the hero name as a fallback."""
    hue = hash(name) % 360
    r = int(40 + 30 * (hue % 3))
    g = int(40 + 30 * ((hue // 3) % 3))
    b = int(40 + 30 * ((hue // 9) % 3))
    img = Image.new("RGB", FRAME_SIZE, (r, g, b))
    draw = ImageDraw.Draw(img)
    label = name.replace("_", " ")
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((FRAME_SIZE[0] - tw) / 2, (FRAME_SIZE[1] - th) / 2),
        label,
        fill="white",
        font=font,
    )
    return img


def _load_hero_image(hero_name: str) -> Image.Image:
    path = os.path.join(HERO_PICS_DIR, f"{hero_name.lower()}.png")
    if os.path.exists(path):
        return Image.open(path).resize(FRAME_SIZE, Image.Resampling.LANCZOS)
    return _make_placeholder(hero_name)


class HeroDrafterButton(tk.Frame):
    def __init__(
        self, hero: Hero, runner: DesktopProgramRunner, master=None, *args, **kwargs
    ):
        super().__init__(
            master, *args, **kwargs, width=FRAME_SIZE[0], height=FRAME_SIZE[1]
        )

        self.hero = hero
        self.runner = runner

        self.image = ImageTk.PhotoImage(_load_hero_image(hero.name))

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

        # Bind mouse wheel events to propagate to parent canvas
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas_frame.bind("<MouseWheel>", self._on_mousewheel)

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

    def _on_mousewheel(self, event: "tk.Event[tk.Misc]") -> None:
        """Propagate mouse wheel events to the parent canvas for scrolling"""
        parent = self.master
        while parent and not hasattr(parent, "on_mousewheel"):
            parent = parent.master  # type: ignore[union-attr]
        if parent:
            handler = getattr(parent, "on_mousewheel", None)
            if handler is not None:
                handler(event)

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
