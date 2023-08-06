import tkinter as tk
from tkinter import ttk

from tempcf.Observable import Observable
from tempcf.EntryValidation import Validator


class FilterList(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        self._interactables = []
        self.filterListObservable = Observable()
        self.window = tk.Frame(self.parent)
        self.topContainer = tk.Frame(self.window)
        self.applyBtn = tk.Button(self.topContainer, text="Apply Filter", state=tk.DISABLED, command=self.applyFilter)
        self.deleteBtn = tk.Button(self.topContainer, text="Delete Filter", state=tk.DISABLED, command=self.removeFilter)
        self.applyBtn.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.deleteBtn.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.topContainer.pack(side=tk.TOP, fill=tk.X)
        
        self.table = ttk.Treeview(self.window, show="tree", selectmode="browse")
        self.scrollbar = ttk.Scrollbar(self.table, orient="vertical", command=self.table.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscrollcommand=self.scrollbar.set)
        self.table.bind("<ButtonRelease-1>", self.selectedFilter)
        self.table.pack(fill=tk.BOTH, expand=1)
        
        self.bottomContainer = tk.Frame(self.window)
        self.selDelContainer = tk.Frame(self.bottomContainer)
        self.deleteDataBtn = tk.Button(self.selDelContainer, text="Delete Selected Data", state=tk.DISABLED, command=self.deleteSelectedData)
        self.replaceContainer = tk.Frame(self.bottomContainer)
        self.replaceDataBtn = tk.Button(self.replaceContainer, text="Replace Selected Data", state=tk.DISABLED, command=self.replaceSelectedData)
        self.selectFilteredDataBtn = tk.Button(self.selDelContainer, text="Select Filtered Data", state=tk.DISABLED, command=self.selectFilteredData)
        self.replacingValue = tk.DoubleVar()
        self.replaceField = tk.Entry(self.replaceContainer, width=22, textvariable=self.replacingValue, validate="key", validatecommand=(self.window.register(self.floatCheck), "%P"), state=tk.DISABLED)
        self.selectFilteredDataBtn.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.deleteDataBtn.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.selDelContainer.pack(fill=tk.X)
        self.replaceDataBtn.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.replaceField.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.replaceContainer.pack(fill=tk.X)
        self.bottomContainer.pack(side=tk.BOTTOM)
        
        self.window.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        
        # List of tk elements that may become active/interactable with once a dataset is loaded in
        self._interactables.extend([self.applyBtn, self.deleteBtn, self.deleteDataBtn, self.replaceDataBtn, self.selectFilteredDataBtn])
        
        self.parent.parent.bind("r", self.sc_replace)
        self.parent.parent.bind("d", self.sc_delete)
        self.parent.parent.bind("<Delete>", self.sc_delete)
        self.parent.parent.bind("<BackSpace>", self.sc_delete)
    
    def selectFilteredData(self):
        self.filterListObservable.callbacks["selectFilteredData"]()
    
    def sc_delete(self, ev):
        if self.deleteDataBtn.cget("state") == "normal":
            self.deleteSelectedData()
    
    def deleteSelectedData(self):
        self.filterListObservable.callbacks["deleteSelectedData"]()
    
    def sc_replace(self, ev):
        if self.replaceDataBtn.cget("state") == "normal":
            self.replaceSelectedData()
    
    def replaceSelectedData(self):
        self.filterListObservable.callbacks["replaceSelectedData"](self.replacingValue.get())
    
    def selectedFilter(self, ev):
        item_id = self.table.focus()
        try:
            int(item_id)
        except ValueError:
            self.applyBtn.config(state=tk.DISABLED)
            self.deleteBtn.config(state=tk.DISABLED)
            return
        else:
            self.applyBtn.config(state=tk.NORMAL)
            self.deleteBtn.config(state=tk.NORMAL)
    
    def addFilter(self, filter):
        table_elements = len(self.table.get_children())
        self.table.insert("", table_elements, text=f"{filter.getIdentifier()}: {filter.getName()}", iid=filter.getIdentifier(), open=True)
        for key, value in filter.getUserParams().items():
            self.table.insert(filter.getIdentifier(), tk.END, text=f"{key}: {value}")
    
    def applyFilter(self):
        item_id = self.table.focus()
        try:
            int(item_id)
        except ValueError:
            return
        else:
            filter_identifier = int(self.table.item(item_id)["text"].split(":")[0])
            self.filterListObservable.callbacks["applyFilter"](filter_identifier)
    
    def postFilterAction(self, filteredCount):
        tk.messagebox.showinfo(title="Filtered Values", message=f"{filteredCount} value(s) were highlighted by the filter.")
        self.selectFilteredDataBtn.config(state=tk.NORMAL)
    
    def floatCheck(self, value):
        result = Validator('float').validate(value)
        return result
    
    def removeFilter(self):
        item_id = self.table.focus()
        try:
            int(item_id)
        except ValueError:
            return
        else:
            item_index = self.table.index(item_id)
            self.table.delete(item_id)
            self.filterListObservable.callbacks["removeFilter"](item_index)

    def clearList(self):
        self.table.delete(*self.table.get_children())
    
    def activateSelectionButtons(self):
        self.deleteDataBtn.config(state=tk.NORMAL)
        self.replaceDataBtn.config(state=tk.NORMAL)
        self.replaceField.config(state=tk.NORMAL)
        
    def deactivateSelectionButtons(self):
        self.deleteDataBtn.config(state=tk.DISABLED)
        self.replaceDataBtn.config(state=tk.DISABLED)
        self.replaceField.config(state=tk.DISABLED)
    
    def deactivateInteractions(self):
        for el in self._interactables:
            el.config(state=tk.DISABLED)
