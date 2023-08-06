from functools import partial
from pathlib import Path

import re
import tkinter as tk
import tkinter.filedialog as filedialog

from tempcf.HelpDialog import HelpDialog
from tempcf.Observable import Observable
from tempcf.MetadataDialog import MetadataDialog
from tempcf.Utils import resourcePath
from tempcf.AboutDialog import AboutDialog
from tempcf.FilterConfigure import FilterConfigure
from tempcf.FilterContainer import FilterContainer
import tempcf.FileTypes as ft


class MainToolbar(tk.Frame):
    # A dictionary of export options that are enabled, dependent on the type of dataset opened
    _AVAILABLE_OPTIONS = {
        "wide": [0,3],
        ft.NTGS: [0,3],
        ft.GTNP: [0,3],
        "netcdf": [],
        ft.GEOPREC: [0, 1, 2,3],
        ft.HOBO: [0,3],
        ft.RBR: [0,3],
        "database": []
    }

    def __init__(self, parent):
        self.filepath = Observable(None)
        self.exportPath = Observable(None)
        self.logPath = Observable(None)
        self.parent = parent
        self.toolbarObservable = Observable()
        self.program_menu = tk.Menu(parent)
        self.file_dropdown = tk.Menu(self.program_menu, tearoff=0)
        self.filters_dropdown = tk.Menu(self.program_menu, tearoff=0)
        self.depths_dropdown = tk.Menu(self.program_menu, tearoff=0)
        self.file_open_type_dropdown = tk.Menu(self.file_dropdown, tearoff=0)
        self.export_type_dropdown = tk.Menu(self.file_dropdown, tearoff=0)
        self.help_dropdown = tk.Menu(self.program_menu, tearoff=0)
        self._last_save_file = None
        self._last_open_file = None

        # Order matters here! The order in which these menu options are added correspond to the indices in "_AVAILABLE_OPTIONS"
        # so that they can be toggled easily depending on what is selected. If you change the order here, change the index in the dictionary as well.
        # The array of indices are the export options available, which is dependent on the import option selected.

        # File Menu
        self.file_open_type_dropdown.add_command(label="NTGS Database (CSV)", command=partial(self.openFile, ft.NTGS))
        self.file_open_type_dropdown.add_command(label="GTN-P Database", command=partial(self.openFile, ft.GTNP))
        self.file_open_type_dropdown.add_command(label="GeoPrecision (CSV)", command=partial(self.openFile, ft.GEOPREC))
        self.file_open_type_dropdown.add_command(label="HOBO (HOBOware CSV)", command=partial(self.openFile, ft.HOBO))
        self.file_open_type_dropdown.add_command(label="RBR (dat, hex, rsk, xls(x))", command=partial(self.openFile, ft.RBR))
        self.file_open_type_dropdown.add_command(label="Database", state=tk.DISABLED)

        self.export_type_dropdown.add_command(label="NTGS Database", state=tk.DISABLED, command=partial(self.saveFile, ft.NTGS))  # Export Option 0
        self.export_type_dropdown.add_command(label="GeoPrecision (GP5W CSV)", state=tk.DISABLED, command=partial(self.saveFile, ft.GP5W))  # Export Option 1
        self.export_type_dropdown.add_command(label="GeoPrecision (FG2 CSV)", state=tk.DISABLED, command=partial(self.saveFile, ft.FG2))  # Export Option 2
        self.export_type_dropdown.add_command(label="GTN-P Database", state=tk.DISABLED, command=partial(self.saveFile, ft.GTNP))  # Export Option 3
        self.export_type_dropdown.add_command(label="NetCDF", state=tk.DISABLED)

        self.file_dropdown.add_cascade(label="Open Data Source", menu=self.file_open_type_dropdown)
        self.file_dropdown.add_command(label="Close Data Source", command=self.closeFile)
        self.file_dropdown.add_separator()
        self.file_dropdown.add_command(label="Apply Changes From Log File", state=tk.DISABLED, command=self.importLog)
        self.file_dropdown.add_separator()
        self.file_dropdown.add_cascade(label="Export Changes", menu=self.export_type_dropdown)
        self.file_dropdown.add_separator()
        self.file_dropdown.add_command(label="View file metadata", command=self.showMetadata)
        self.file_dropdown.add_command(label="Quit", command=parent.quit)

        self.program_menu.add_cascade(label="File", menu=self.file_dropdown)
        self.program_menu.add_cascade(label="Filters", menu=self.filters_dropdown)
        self.program_menu.add_cascade(label="Depths", menu=self.depths_dropdown)
        self.program_menu.add_cascade(label="Help!", menu=self.help_dropdown)

        # Help menu
        self.help_dropdown.add_command(label="How to Use", command=self.showHelp)
        self.help_dropdown.add_command(label="About", command=self.showAbout)
        self.help_dropdown.add_command(label="Open Demo Dataset", command=self.demoFile)

        self.parent.config(menu=self.program_menu)

    def loadDepths(self, depths):
        self.depthStates = []
        for depth in depths:
            func = self.getToggleFunction(depth)
            state = tk.BooleanVar()
            state.set(True)
            self.depths_dropdown.add_checkbutton(label=depth, indicatoron=True, variable=state, command=func)
            self.depthStates.append(state)
        self.depths_dropdown.add_command(label="View all", command=self.toggleAllDepths)
        self.depths_dropdown.add_command(label="View none", command=self.toggleNoDepths)
        self.depths_dropdown.add_command(label="Change Depths", command=self.changeDepths)

    def changeDepths(self):
        self.toolbarObservable.callbacks["renameDepths"]()

    def getToggleFunction(self, depth):
        def toggle():
            self.toolbarObservable.callbacks["toggleDepth"](depth)
        return toggle

    def toggleAllDepths(self):
        for state in self.depthStates:
            state.set(True)
        self.toolbarObservable.callbacks["toggleAllDepths"]()

    def toggleNoDepths(self):
        for state in self.depthStates:
            state.set(False)
        self.toolbarObservable.callbacks["toggleNoDepths"]()

    def showAbout(self):
        AboutDialog(self.parent)

    def showHelp(self):
        HelpDialog(self.parent)

    def showMetadata(self):
        text = self.toolbarObservable.callbacks["getMetadata"]()
        MetadataDialog(self.parent, text)

    def getFilterConfiguration(self, filter):
        confirmed_values = FilterConfigure(self.parent).display(filter.getName(), filter.getParams(), filter.getHelpText())
        if confirmed_values:
            new_filter = FilterContainer(filter.getName(), filter.getFunction(), filter.getParams(), filter.getHelpText())
            new_filter.setUserParams(confirmed_values)
            self.toolbarObservable.callbacks["addFilter"](new_filter)

    def loadFilters(self, filters):
        for filter in filters:
            self.filters_dropdown.add_command(label=filter.getName(), command=partial(self.getFilterConfiguration, filter))

    def clearFilters(self):
        self.filters_dropdown.delete(0, self.filters_dropdown.index(tk.END) + 1 if self.filters_dropdown.index(tk.END) else 0)

    def clearDepths(self):
        self.depths_dropdown.delete(0, self.depths_dropdown.index(tk.END) + 1 if self.depths_dropdown.index(tk.END) else 0)

    def toggleExports(self, tkState, fileType=None):
        if fileType is None:
            # Likely that this runs when you want to disable all export options.
            menuLength = self.export_type_dropdown.index(tk.END)
            for index in range(menuLength + 1):
                self.export_type_dropdown.entryconfigure(index, state=tkState)
        else:
            for index in self._AVAILABLE_OPTIONS[fileType]:
                self.export_type_dropdown.entryconfigure(index, state=tkState)

    def saveFile(self, exportType):
        init_name = re.sub(r"([^\.]+)\.(.*)$", r"\1_export.\2", Path(self.filepath.get()).name) if self.filepath.get() else None
        init_dir = Path(self.exportPath.get()).parent if self.exportPath.get() else None
        exportPath = filedialog.asksaveasfilename(
            parent=self.parent,
            title="Export Data",
            initialdir=init_dir,
            initialfile=init_name,
            filetypes=[("CSV Files", "*.csv"),
                       ("Text Files", "*.txt"),
                       ("All files", "*"),]
        )
        if exportPath:
            self.exportPath.callbacks["exportData"](exportPath, exportType)
            self.exportPath.data = exportPath
        else:
            return

    def importLog(self):
        logPath = filedialog.askopenfilename(
            parent=self.parent,
            title="Import Log",
            filetypes=[("Log Files", "*.log"), ("All Files", "*")]
        )
        if logPath:
            self.toolbarObservable.callbacks["importLog"](logPath)
        else:
            return

    def openFile(self, dataType):
        init_dir = Path(self.filepath.get()).parent if self.filepath.get() else None
        filetypes = ft.file_open_extensions(dataType)
        filepath = filedialog.askopenfilename(
            parent=self.parent,
            initialdir=init_dir,
            title="Select Dataset",
            filetypes=filetypes
        )
        if filepath:
            self.doOpenFile(dataType, filepath)
        else:
            return

    def doOpenFile(self, dataType, filepath):
        if self.filepath.get():
            self.closeFile()
        self.toolbarObservable.callbacks["setImportType"](dataType)
        self.toggleExports(tk.NORMAL, dataType)
        self.file_dropdown.entryconfigure(3, state=tk.NORMAL)  # tkinter is awful here, 3 is referring to the "Import Log File" option in the menu (separators take up an index)
        self.filepath.set(filepath)

    def closeFile(self):
        self.file_dropdown.entryconfigure(3, state=tk.DISABLED)
        self.toggleExports(tk.DISABLED)
        self.filepath.set(-1)
        self.filepath.unset()

    def demoFile(self):
        self.doOpenFile("geoprecision", resourcePath("assets/demo_GP5W.txt"))
