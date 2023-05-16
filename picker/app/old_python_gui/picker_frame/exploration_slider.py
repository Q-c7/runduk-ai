import tkinter as tk
from tkinter import ttk

from picker.app.old_python_gui.picker_frame.prediction_display import PredictionDisplay


class ExplorationSlider(tk.Frame):
    def __init__(self, predictor_widget: PredictionDisplay | None = None, master=None):
        super().__init__(master)
        self.predictor_widget = predictor_widget

        # Initialize slider's current value
        self.current_value = tk.DoubleVar()

        # Label to the left of the slider
        slider_label = ttk.Label(self, text="No\npreferences")
        slider_label.grid(column=0, row=0)  # sticky='w')

        # The slider itself
        self.slider = ttk.Scale(
            self,
            from_=0,
            to=1,
            orient="horizontal",
            command=self.slider_changed,
            variable=self.current_value,
        )
        self.slider.grid(column=1, row=0)

        # label for the slider
        slider_label_2 = ttk.Label(self, text="Strong\npreferences")

        slider_label_2.grid(
            column=2,
            row=0,
            # sticky='w'
        )

    def slider_changed(self, event):
        if self.predictor_widget is None:
            return
        self.predictor_widget.update_preference_coefficient(self.current_value.get())


if __name__ == "__main__":
    root = tk.Tk()
    slider_demo = ExplorationSlider(master=root)
    slider_demo.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
