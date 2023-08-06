from tkinter import ttk
import tkinter as tk


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.bind("<Enter>", lambda e: self._bound_to_mousewheel(e, canvas))
        self.bind("<Leave>", lambda e: self._unbound_to_mousewheel(e, canvas))

    def _bound_to_mousewheel(self, event, canvas):
        canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))

    def _unbound_to_mousewheel(self, event, canvas):    
        canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event, canvas):    
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")


if __name__ == "__main__":
    root = tk.Tk()
    frame = ScrollableFrame(root)
    frame.pack(fill="both", expand=True)
    for i in range(50):
        ttk.Label(frame.scrollable_frame, text="Sample scrolling label").pack()
    root.mainloop()