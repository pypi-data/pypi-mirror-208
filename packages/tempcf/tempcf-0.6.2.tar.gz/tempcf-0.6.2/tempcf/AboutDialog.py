import tkinter as tk

from functools import partial
from PIL import Image, ImageTk

from tempcf.PopoutDialog import PopoutDialog
from tempcf.Utils import resourcePath

from tempcf._version import __version__


class AboutDialog(PopoutDialog):
    wikiLink = "https://permafrostnet.gitlab.io/permafrost-tempcf/"
    repoLink = "https://gitlab.com/permafrostnet/permafrost-tempcf"
    about = f"""
tempcf version {__version__}\n\n
This software is meant to improve the useability of permafrost data by allowing data creators to visually flag, assess, and take action on suspicious measurements.\n
It includes a library of functions for identifying suspicious data, and a GUI to assist in the cleaning of the data.\n
For more information, visit the documentation at: {wikiLink}\n
or contribute and report issues at: {repoLink}
    """

    def __init__(self, parent):
        PopoutDialog.__init__(self, parent)
        self.dialog.title("About Permafrost TempCF")
        self.image = ImageTk.PhotoImage(Image.open(resourcePath("assets/permafrostnet_logo_text.png")).resize((408, 266), Image.BILINEAR))
        self.imgContainer = tk.Label(self.frame, image=self.image)
        self.message = tk.Message(self.frame, text=self.about, width=550)
        self.wikiBtn = tk.Button(self.frame, text="Copy Documentation Link", command=partial(self.copyToClipboard, self.wikiLink), width=35)
        self.repoBtn = tk.Button(self.frame, text="Copy Repository Link", command=partial(self.copyToClipboard, self.repoLink), width=35)

        self.imgContainer.pack(fill=tk.Y, pady=10)
        self.message.pack(fill=tk.BOTH, expand=1, padx=20)
        self.wikiBtn.pack(padx=20)
        self.repoBtn.pack(padx=20, pady=10)
        self.dialog.grab_set()
        self.dialog.focus_force()
        self.dialog.wait_window()

    def copyToClipboard(self, text):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        self.parent.update()
