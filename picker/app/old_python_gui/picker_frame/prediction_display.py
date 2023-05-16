import tkinter as tk
import time

from collections import defaultdict

from picker.app.constants import HEROES

PREDICTOR_SIZE = (700, 400)
PREFERENCE_CONSTANT = 0.1
TIMEOUT = 0.1


class PredictionDisplay(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs, background="blue")
        self.predictions = {}
        self.preferences = defaultdict(list)
        self.preference_coefficient: float = 0.0
        self._last_update = time.perf_counter()

        self.canvas = tk.Canvas(self, width=PREDICTOR_SIZE[0], height=PREDICTOR_SIZE[1])
        self.scroll_area = tk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.canvas.yview
        )

        self.scroll_area.config(command=self.canvas.yview)

        self.rect_frame = tk.Frame(self.canvas)

        self.canvas.create_window((0, 0), window=self.rect_frame, anchor="nw")

        self.scroll_area.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

    def update_preds(self, new_preds: dict[str, float]):
        self.predictions = new_preds
        self.update_ui()

    def update_preferences(self, new_preferences: dict[str, list[int]]):
        self.preferences = defaultdict(list)
        for k, v in new_preferences.items():
            self.preferences[int(k)].extend(v)

    def update_preference_coefficient(self, new_coef: float):
        self.preference_coefficient = new_coef
        if self._last_update < time.perf_counter() - TIMEOUT:
            self.update_ui()
            self._last_update = time.perf_counter()

    def _recalculate_scores(self) -> list[list[tuple[int, float]]]:
        adjusted_preds: list[list[tuple[int, float]]] = [[], [], [], [], []]

        for hero_id, pred_score in self.predictions.items():
            assert 0 < hero_id < len(HEROES), hero_id
            hero = HEROES[hero_id]
            additional_prefs = (
                self.preferences[hero_id] if hero_id in self.preferences else []
            )

            all_roles = set(hero.pos + hero.alt_pos + additional_prefs)

            for role in all_roles:
                is_preferred = role in additional_prefs
                preference = PREFERENCE_CONSTANT * self.preference_coefficient
                total_score = pred_score + preference * is_preferred

                adjusted_preds[role - 1].append((hero_id, total_score))

        for role in range(5):
            adjusted_preds[role - 1] = sorted(
                adjusted_preds[role - 1], key=lambda x: -x[1]
            )

        return adjusted_preds

    def _redraw(self, adjusted_preds: list[list[tuple[int, float]]]):
        assert len(adjusted_preds) == 5

        # Clear existing rectangles
        for widget in self.rect_frame.winfo_children():
            widget.destroy()

        # Create new rectangles
        current_rows = [0] * 5
        for col in range(5):
            for hero_id, score in adjusted_preds[col]:
                row = current_rows[col]

                rect_frame = tk.Frame(self.rect_frame, relief=tk.SOLID, borderwidth=1)

                rect_label = tk.Label(
                    rect_frame, text=f"{HEROES[hero_id].name}\n{score:.3f}"
                )
                rect_label.pack()

                rect_frame.grid(row=row, column=col, padx=5, pady=5)

                current_rows[col] += 1

        self.canvas.update_idletasks()

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all"), yscrollcommand=self.scroll_area.set
        )

    def update_ui(self):
        self._redraw(self._recalculate_scores())

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
