import tkinter as tk

from picker.app.old_python_gui.picker_frame import PickerFrame
from picker.app.old_python_gui.team_frame import TeamFrame


class MyApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1400x700")

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
            # print('KWARG', kwargs['to_predictor'])
            self.frames["PickerFrame"].runner.prediction_display.update_preferences(
                kwargs["to_predictor"]
            )

        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    root = MyApp()
    root.mainloop()
