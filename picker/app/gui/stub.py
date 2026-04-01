from abc import abstractmethod

import tkinter as tk


class AbstractFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def update_ui(self):
        pass
