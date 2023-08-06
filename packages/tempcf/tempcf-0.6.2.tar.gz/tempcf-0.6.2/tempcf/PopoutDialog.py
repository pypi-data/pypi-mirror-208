import tkinter as tk

from tempcf.Utils import resourcePath


class PopoutDialog():
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.iconbitmap(resourcePath("assets/permafrostnet_logo.ico"))
        self.frame = tk.Frame(self.dialog)
        self.frame.pack()
