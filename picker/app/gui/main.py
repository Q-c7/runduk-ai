import tkinter as tk

from picker.app.gui.picker_frame import PickerFrame
from picker.app.gui.team_frame import TeamFrame


class MyApp(tk.Tk):
    def __init__(self, model_path="latest", *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1800x700")
        self.model_path = model_path

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (PickerFrame, TeamFrame):
            page_name = F.__name__
            if F == PickerFrame:
                frame = F(self.container, model_path=self.model_path)
            else:
                frame = F(self.container)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("TeamFrame")

    def show_frame(self, page_name, **kwargs):
        if page_name == "PickerFrame" and "to_predictor" in kwargs:
            assert self.frames["PickerFrame"].runner.prediction_display is not None
            self.frames["PickerFrame"].runner.prediction_display.update_preferences(
                kwargs["to_predictor"]
            )

        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Dota 2 Hero Picker GUI")
    parser.add_argument("--model", default="latest", help="Path to the model file (default: latest)")
    args = parser.parse_args()
    
    root = MyApp(model_path=args.model)
    root.mainloop()
