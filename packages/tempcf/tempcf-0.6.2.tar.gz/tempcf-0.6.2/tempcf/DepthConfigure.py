import tkinter as tk
from typing import Optional

from tempcf.PopoutDialog import PopoutDialog
from tempcf.EntryValidation import Validator
from tempcf.ScrollableFrame import ScrollableFrame


class DepthConfigure(PopoutDialog):

    def __init__(self, parent):
        PopoutDialog.__init__(self, parent)
        self.dialog.geometry("400x500")
        self.dialog.title("Rename Depths")
        self.newDepthNames = {}
        
        self.depthContainer = ScrollableFrame(self.frame)
        self.bottomFrame = tk.Frame(self.frame, width=300, height=50, pady=5, padx=100)
        self.error = tk.Message(self.bottomFrame, text="", font=("Arial", 14), fg="red", pady=5, width=400)
        self.btn = tk.Button(self.bottomFrame, text="OK", padx=15, command=lambda: self.ok(), state=tk.DISABLED)

    def ok(self):
        self.dialog.destroy()
    
    def cancel(self):
        self.newDepthNames = None
        self.dialog.destroy()
    
    def floatCheck(self, value):
        result = Validator("float").validate(value)
        if result:
            self.error.config(text="")
            self.btn.config(state=tk.NORMAL)
        else:
            self.error.config(text="Invalid value(s)!\nThe depth values require a float/double value.")
            self.btn.config(state=tk.DISABLED)
        return result
    
    def display(self, depths) -> "Optional[dict[str, tk.StringVar]]":
        message = tk.Label(self.frame, text="For each of the sensors, please enter the sensor depth in metres.")
        message.pack(pady=10)

        first = True
        for depth in depths:
            columnName = tk.StringVar()
            columnName.set(depth)
            label = tk.Message(self.depthContainer.scrollable_frame, text=depth, width=200)
            label.pack()
            depthEntry = tk.Entry(self.depthContainer.scrollable_frame, 
                                  textvariable=columnName,
                                  validate="key",
                                  validatecommand=(self.dialog.register(self.floatCheck), "%P"))
            depthEntry.bind("<Return>", lambda e: self.ok())
            if first:
                first = False
                depthEntry.focus_force()
            self.newDepthNames[str(depth)] = columnName
            depthEntry.pack(pady=5)

        self.depthContainer.pack()
        self.bottomFrame.pack(after=self.depthContainer)
        self.error.pack()
        self.btn.pack()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        self.dialog.wait_window()
        
        return self.newDepthNames
