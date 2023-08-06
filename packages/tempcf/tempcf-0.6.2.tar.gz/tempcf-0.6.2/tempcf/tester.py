import tkinter as tk

from tempcf.EntryValidation import Validator


class Example(tk.Frame):
    def __init__(self, parent, depths):

        tk.Frame.__init__(self, parent)
        self.depths = depths
        self.topframe = tk.Frame(self, background="#5f1f1f", width=500, height=50)
        self.midframe = tk.Frame(self, width=500, height=300)
        self.canvas = tk.Canvas(self.midframe, borderwidth=1, background="#111111")
        self.scrollframe = tk.Frame(self)
        self.buttonframe = tk.Frame(self)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.error = tk.Message(self.buttonframe, text="", font=("Arial", 14), fg="red", pady=5, width=400)
        self.btn = tk.Button(self.buttonframe, text="OK", padx=15, command=lambda: self.destroy(), state=tk.DISABLED)

        # Positioning
        self.topframe.pack(side='top', fill='x')
        self.midframe.pack(side='top', fill='x')
        self.canvas.pack(in_=self.midframe, side="left", fill="x", expand=False)
        
        self.canvas.create_window((4,4), window=self.scrollframe, anchor="nw",
                                  tags="self.scrollframe")
        self.buttonframe.pack(after=self.midframe, side="bottom", fill="x", expand=True)
        self.vsb.pack(in_=self.midframe, side="right", fill="y")
        
        self.btn.pack(side="bottom", pady=5)
        self.error.pack(side="bottom", pady=5)

        # Binding
        self.scrollframe.bind("<Configure>", self.onFrameConfigure)

        self.populate()

    def populate(self):
        '''Put in some fake data'''
        message = tk.Label(self.topframe, text="For each of the sensors, please enter the sensor depth in metres.")
        message.pack(pady=10)

        self.newDepthNames = {}
        first = True
        for depth in self.depths:
            columnName = tk.StringVar()
            columnName.set(depth)
            label = tk.Message(self.scrollframe, text=depth, width=200)
            label.pack(fill='x', expand=True)
            depthEntry = tk.Entry(self.scrollframe, textvariable=columnName, validate="key", validatecommand=(self.register(self.floatCheck), "%P"))
            depthEntry.bind("<Return>", func=lambda event: self.destroy())
            if first:
                depthEntry.focus_force()
                first = False
            self.newDepthNames[str(depth)] = columnName
            depthEntry.pack(fill='x', expand=True, pady=5)

    def floatCheck(self, value):
        result = Validator("float").validate(value)
        if result:
            self.error.config(text="")
            self.btn.config(state=tk.NORMAL)
        else:
            self.error.config(text="Invalid value(s)!\nThe depth values require a float/double value.")
            self.btn.config(state=tk.DISABLED)
        return result

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    root=tk.Tk()
    example = Example(root, [1,2,3,4,5,6,7,8,9,10])
    example.pack(side="top", fill="both", expand=True)
    root.mainloop()