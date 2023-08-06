import tkinter as tk
import tkinter.scrolledtext as tkscroll

from tempcf.PopoutDialog import PopoutDialog
from tempcf.EntryValidation import Validator


class FilterConfigure(PopoutDialog):
    def __init__(self, parent):
        PopoutDialog.__init__(self, parent)
        self.dialog.geometry("500x400+250+250")
        self.dialog.title("Configure Filter Values")
        self.edit_dialog = tk.Frame(self.dialog)
        self.initial_vars = {}
        self.confirmed_vars = {}
        self.error_text = tk.Message(self.dialog, text="", font=("Arial", 14), fg="red", pady=5, width=400)
    
    def intCheck(self, value):
        result = Validator('int').validate(value)
        if not result:
            self.error_text.config(text="Invalid value!\nThe field requires a float/double value.")
        else:
            self.error_text.config(text="")
        return result

    def floatCheck(self, value):
        result = Validator('float').validate(value)
        if not result:
            self.error_text.config(text="Invalid value!\nThe field requires a float/double value.")
        else:
            self.error_text.config(text="")
        return result

    def switchForInput(self, parent, var_name, var_type, var_value):
        if var_type == int:
            self.initial_vars[var_name] = tk.IntVar()
            self.initial_vars[var_name].set(var_value)
            return tk.Entry(parent, textvariable=self.initial_vars[var_name], validate="key", validatecommand=(self.dialog.register(self.intCheck), "%P"))
        elif var_type == float:
            self.initial_vars[var_name] = tk.DoubleVar()
            self.initial_vars[var_name].set(var_value)
            return tk.Entry(parent, textvariable=self.initial_vars[var_name], validate="key", validatecommand=(self.dialog.register(self.floatCheck), "%P"))
        elif var_type == str:
            self.initial_vars[var_name] = tk.StringVar()
            self.initial_vars[var_name].set(var_value)
            return tk.Entry(parent, textvariable=self.initial_vars[var_name])
        elif var_type == bool:
            self.initial_vars[var_name] = tk.BooleanVar()
            self.initial_vars[var_name].set(var_value)
            return tk.Checkbutton(parent, variable=self.initial_vars[var_name])
        else:
            self.initial_vars[var_name] = tk.StringVar()
            self.initial_vars[var_name].set(var_value)
            return tk.Entry(parent, textvariable=self.initial_vars[var_name])
    
    def setConfirmedValues(self):
        for k,v in self.initial_vars.items():
            self.confirmed_vars[k] = v.get()
        self.dialog.destroy()
    
    def display(self, name, args, help):
        title = tk.Message(self.dialog, text=name, font=("Courier New", 16), width=400)
        title.pack(side=tk.TOP, fill=tk.X, expand=0)
        info = tkscroll.ScrolledText(self.dialog, width=400, height=10, wrap=tk.WORD)
        info.insert(tk.INSERT, help)
        info.configure(state=tk.DISABLED)
        info.pack(side=tk.TOP, fill=tk.X, padx=10, expand=0, ipady=20)
        for arg in args:
            row_container = tk.Frame(self.dialog)
            label = tk.Message(row_container, text=arg[0], width=200)
            label.pack(side=tk.LEFT)
            entry = self.switchForInput(row_container, arg[0], arg[1], arg[2])
            entry.pack(side=tk.RIGHT)
            row_container.pack(pady=2)
        btn = tk.Button(self.dialog, text="OK", padx=15, command=self.setConfirmedValues)
        btn.pack()
        self.edit_dialog.pack()
        self.error_text.pack()
        self.dialog.grab_set()
        self.dialog.focus_force()
        self.dialog.wait_window()
        return self.confirmed_vars
