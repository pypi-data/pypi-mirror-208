import tkinter as tk

from tempcf.PopoutDialog import PopoutDialog


class TimeZoneConfigure(PopoutDialog):
    _TIMEZONES = ["UTC-12:00", "UTC-11:00", "UTC-10:00", "UTC-09:30", "UTC-09:00", "UTC-08:00", "UTC-07:00", "UTC-06:00", "UTC-05:00", "UTC-04:00", "UTC-03:30", "UTC-03:00", "UTC-02:00", "UTC-01:00",
        "UTC+00:00", "UTC+01:00", "UTC+02:00", "UTC+03:00", "UTC+03:30", "UTC+04:00", "UTC+04:30", "UTC+05:00", "UTC+05:30", "UTC+05:45", "UTC+06:00", "UTC+06:30", "UTC+07:00", "UTC+08:00",
         "UTC+08:45", "UTC+09:00", "UTC+09:30", "UTC+10:00", "UTC+10:30", "UTC+11:00", "UTC+12:00", "UTC+12:45", "UTC+13:00", "UTC+14:00"]
    
    def cancel(self):
        self.tzSelection = None
        self.dialog.destroy()

    def __init__(self, parent):
        PopoutDialog.__init__(self, parent)
        self.dialog.geometry("400x150")
        self.dialog.title("Set Dataset Time Zone")
        
    def display(self):
        message = tk.Label(self.frame, text="Please set the timezone offset for the currently loaded data.")
        message.pack(pady=10)
        self.tzSelection = tk.StringVar()
        self.tzSelection.set(self._TIMEZONES[14])
        self.options = tk.OptionMenu(self.frame, self.tzSelection, *self._TIMEZONES)
        self.options.pack(pady=5)

        btn = tk.Button(self.frame, text="OK", padx=15, command=lambda: self.dialog.destroy())
        btn.pack(pady=10)
        self.dialog.protocol("WM_DELETE_dialog", self.cancel)
        self.dialog.grab_set()
        self.dialog.focus_force()
        self.dialog.wait_window()
        return self.tzSelection.get()[3:] if self.tzSelection is not None else self.tzSelection # Return the slice (of the timezone) or return itself as it was set to None from the cancel
