from PIL import ImageTk

from picker.app.constants import Hero, TKINTER_BIG_FONT
from picker.app.gui.logic.team import TeamManager
from picker.app.gui.picker_frame.hero_drafter_button import FRAME_SIZE, _load_hero_image

import tkinter as tk

from picker.app.gui.stub import AbstractFrame


class HeroAdderButton(AbstractFrame):
    def __init__(self, hero: Hero, manager: TeamManager, master=None, *args, **kwargs):
        super().__init__(
            master, *args, **kwargs, width=FRAME_SIZE[0], height=FRAME_SIZE[1]
        )

        self.hero = hero
        self.manager = manager
        self.pos = manager.get_current_pos()

        self.image = ImageTk.PhotoImage(_load_hero_image(hero.name))

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
