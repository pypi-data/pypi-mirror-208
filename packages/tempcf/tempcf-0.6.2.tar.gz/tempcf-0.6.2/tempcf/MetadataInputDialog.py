import tkinter as tk
from tkinter import ttk
from typing import Optional, Any

from tempcf.PopoutDialog import PopoutDialog
from tempcf.EntryValidation import Validator
from tempcf.ToolTip import CreateToolTip


class MetadataInputDialog(PopoutDialog):

    def cancel(self):
        self.values = None
        self.dialog.destroy()

    def ok(self):
        # Check that all fields are filled
        self.final_values = {key: value.get() for key, value in self.values.items()}
        self.dialog.destroy()

    def __init__(self, parent, metadata: "dict[str, tuple[str, str, Any, Any]]", title: str = "Enter metadata"):
        """_summary_

        Parameters
        ----------
        parent : _type_
            _description_
        metadata : dict[str, tuple[str, str, Any, Any]]
            A dictionary with a key for each metadata field. The value is a tuple with the following values:
            1. The label for the field
            2. An explanation of what's required
            3. The default value for the field
            4. The type of the field (int, float, str)
        title : str, optional
            _description_, by default "Enter metadata"
        """
        self.final_values = None
        self.metadata_dict = metadata
        PopoutDialog.__init__(self, parent)
        self.dialog.geometry("400x600")
        self.dialog.title(title)
        self.values = {}
        self.canvas = tk.Canvas(self.frame, width=600, height=800)
        self.metadataContainer = tk.Frame(self.canvas, width=600, height=800)
        scrollbar = ttk.Scrollbar(self.metadataContainer, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas["yscrollcommand"] = scrollbar.set
        self.error = tk.Message(self.frame, text="", font=("Arial", 14), fg="red", pady=5, width=400)
        self.button_frame = tk.Frame(self.frame, width=300, height=50, pady=5, padx=100)
        self.btn = tk.Button(self.button_frame, text="OK", padx=15, command=lambda: self.ok(), state=tk.DISABLED)
        self.btn_cancel = tk.Button(self.button_frame, text="Cancel", padx=15, command=lambda: self.cancel())
        # self.btn.bind('<Return>', func=lambda: self.dialog.destroy)

    def makeCheck(self, checkType, paramName="parameter"):

        def checkFunction(value):
            result = Validator(checkType).validate(value)
            if result:
                self.error.config(text="")
                self.btn.config(state=tk.NORMAL)
            else:
                self.error.config(text=f"Invalid value(s)!\nThe {paramName} must be a {str(checkType)} value.")
                self.btn.config(state=tk.DISABLED)

            return result

        return checkFunction

    def display(self) -> "Optional[dict[str, tk.StringVar]]":
        message = tk.Label(self.frame, text="For each of the items, please enter a value. ")
        message.pack(pady=10, padx=5)

        for key, value in self.metadata_dict.items():
            # Create a string variable with identifier for the field
            columnName = tk.StringVar()
            initialValue = "" if value[3] is None else value[3]
            columnName.set(initialValue)

            # Create a label and tooltip for the field
            label = tk.Message(self.metadataContainer, text=value[0], width=400)
            label.pack(padx=50)
            CreateToolTip(label, text=value[1])

            # Create an entry field for the field
            checkType = value[2]
            checkFunction = self.makeCheck(checkType, paramName=value[0])
            depthEntry = tk.Entry(self.metadataContainer, textvariable=columnName,
                                  validate="all", validatecommand=(self.dialog.register(checkFunction), "%P"))
            depthEntry.bind("<Return>", func=lambda event: self.ok())
            self.values[key] = columnName
            depthEntry.pack(pady=5)

        self.canvas.pack(fill='x', expand=False)
        self.metadataContainer.pack(fill='x', expand=False)
        self.error.pack(fill='x', expand=False)
        self.button_frame.pack(fill='x', expand=True)
        self.btn.grid(row=0, column=0, padx=30)
        self.btn_cancel.grid(row=0, column=3, padx=30)
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        self.dialog.grab_set()
        self.dialog.focus_force()
        self.dialog.wait_window()

        return self.final_values


if __name__ == "__main__":
    root = tk.Tk()
    metadata = {"dim": ("depth in metres", 'float', None), "t_bar": ("tempberate in baroms", float, 0.0), "inf": ("some info", 'str', 'message')}
    vals = MetadataInputDialog(root, metadata).display()
    if vals is not None:
        #print([(item, val.get()) for item, val in vals.items()])
        print(vals)

