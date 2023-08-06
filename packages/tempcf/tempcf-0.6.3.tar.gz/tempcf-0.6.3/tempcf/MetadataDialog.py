from tempcf.ScrollableFrame import ScrollableFrame
from tempcf.Utils import resourcePath

import tkinter as tk
import tkinter.scrolledtext as tkst


class MetadataDialog(tk.Toplevel):
     
    def __init__(self, parent=None, text=""):
         
        super().__init__(master=parent)
        self.title("Metadata")
        self.iconbitmap(resourcePath("assets/permafrostnet_logo.ico"))
        self.geometry("600x800")
        label = tk.Label(self, text="This metadata was found:")
        label.pack()
        self._fill(text)
        self._focus()

    def _fill(self, text):
        info = tkst.ScrolledText(self, width=600, height=800, wrap=tk.WORD)
        info.insert(tk.INSERT, text)
        info.configure(state=tk.DISABLED)
        info.pack(side=tk.TOP, fill=tk.X, padx=10, expand=0, ipady=20)

    def _focus(self):
        self.grab_set()
        self.focus_force()
        self.wait_window()
        

 
