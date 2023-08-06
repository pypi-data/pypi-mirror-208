from functools import partial
import tkinter as tk

from tempcf.PopoutDialog import PopoutDialog


class HelpDialog(PopoutDialog):
    documentationLink = "https://permafrostnet.gitlab.io/permafrost-tempcf/"
    help = f"""
Select data by clicking and dragging the cursor to draw around a selection of points.
Highlight data by applying a filter to select according to the filter specifications.
Temperature values at depths can be toggled on and off. When a depth is toggled off, it will be excluded from drawn and filter selections.

Shortcuts:
CTRL + W - Closes the current file
CTRL + R  - Replaces selected data with the specified value in the input area
CTRL + D  - Deletes (sets the data to NaN values) selected data

For full documentation, see {documentationLink}.
    """

    def __init__(self, parent):
        PopoutDialog.__init__(self, parent)
        self.dialog.title("Permafrost TempCF Help")
        self.message = tk.Message(self.frame, text=self.help, width=600)
        self.wikiBtn = tk.Button(self.frame, text="Copy Documentation Link", command=partial(self.copyToClipboard, self.documentationLink), width=35)
        self.message.pack(fill=tk.BOTH, expand=1, padx=20)
        self.wikiBtn.pack(padx=20, pady=20)
        self.dialog.grab_set()
        self.dialog.focus_force()
        self.dialog.wait_window()

    def copyToClipboard(self, text):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        self.parent.update()
