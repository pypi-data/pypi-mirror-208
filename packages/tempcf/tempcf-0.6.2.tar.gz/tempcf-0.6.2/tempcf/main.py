from pathlib import Path
import tkinter as tk
import logging

import tempcf.LogParser as lp

from tempcf.ActionLogger import ActionLogger
from tempcf.Dataframe import Dataframe
from tempcf.DepthConfigure import DepthConfigure
from tempcf.ExportType import get_exporter
from tempcf.FilterControl import FilterControl
from tempcf.MetadataInputDialog import MetadataInputDialog
from tempcf.FilterList import FilterList
from tempcf.GraphView import GraphView
from tempcf.MainToolbar import MainToolbar
from tempcf.TimeZoneConfigure import TimeZoneConfigure
from tempcf.Utils import resourcePath

from tempcf._version import __version__

logger = logging.getLogger(__name__)


class MainWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.options = MainToolbar(parent)
        self.graphView = GraphView(self)
        self.filterView = FilterList(self)
        self.filterControl = FilterControl()
        self.tableData = Dataframe()
        self.actionLogger = ActionLogger(__version__)
        self.setCallbacks()

    def setCallbacks(self):
        self.options.filepath.setCallback("fileChange", self.fileChange)
        self.options.exportPath.setCallback("exportData", self.exportData)
        self.options.toolbarObservable.setCallback("toggleDepth", self.toggleDepth)
        self.options.toolbarObservable.setCallback("toggleAllDepths", self.toggleAllDepths)
        self.options.toolbarObservable.setCallback("toggleNoDepths", self.toggleNoDepths)
        self.options.toolbarObservable.setCallback("addFilter", self.addFilter)
        self.options.toolbarObservable.setCallback("setImportType", self.setDataImportType)
        self.options.toolbarObservable.setCallback("importLog", self.importLog)
        self.options.toolbarObservable.setCallback("renameDepths", self.renameDepths)
        self.options.toolbarObservable.setCallback("getMetadata", self.getMetadata)
        self.tableData.dataframeObservable.setCallback("loadedData", self.loadedData)
        self.tableData.dataframeObservable.setCallback("loadedDepths", self.loadedDepths)
        self.tableData.dataframeObservable.setCallback("changedData", self.changedData)
        self.tableData.dataframeObservable.setCallback("logAction", self.logAction)
        self.filterControl.filterCntrlObservable.setCallback("loadFilters", self.loadFilters)
        self.filterControl.filterCntrlObservable.setCallback("clearFilters", self.clearFilterList)
        self.filterView.filterListObservable.setCallback("removeFilter", self.removeFilter)
        self.filterView.filterListObservable.setCallback("applyFilter", self.applyFilter)
        self.filterView.filterListObservable.setCallback("selectFilteredData", self.selectFilteredData)
        self.filterView.filterListObservable.setCallback("deleteSelectedData", self.deleteSelectedData)
        self.filterView.filterListObservable.setCallback("replaceSelectedData", self.replaceSelectedData)

        self.tableData.select_i.setCallback("redrawSelectablePoints", self.redrawPoints)
        self.tableData.filter.setCallback("redrawSelectablePoints", self.redrawPoints)
        self.graphView.select_i.setCallback("updateLassoSelection", self.updateLassoSelection)
        self.tableData.depthMask.setCallback("redrawSelectablePoints", self.redrawPoints)

    def setDataImportType(self, importType):
        self.tableData.setDataType(importType)

    def fileChange(self, filepath):
        if filepath == -1:
            self.closeFile(filepath)
            self.updateTitle()
            return
        if self.tableData.getActiveFile():
            self.closeFile(filepath)
        try:
            logger.warning(f"Opening {filepath}")
            self.tableData.setFile(filepath)
            self.actionLogger.setFile(Path(filepath).name)
            self.updateTitle(f"tempcf - {Path(filepath).name}")
        except TypeError as err:
            logger.exception(err)
            self.options.closeFile()
            tk.messagebox.showerror(title="File Type Error", message=err)
        except ValueError as err:
            logger.exception(err)
            self.options.closeFile()
            tk.messagebox.showerror(title="File Reading Error", message=err)
        except Exception as err:
            logger.exception(err)
            self.options.closeFile()
            tk.messagebox.showerror(title="File Reading Error", message="The file was unable to be read.\nEnsure that the file is well formed, formatted, and is the correct type.\nCheck the log for more detail.")

    def closeFile(self, filepath):
        self.graphView.closeGraph()
        self.tableData.resetSelection()
        self.options.clearFilters()
        self.options.clearDepths()
        self.filterView.deactivateInteractions()
        self.filterControl.clearFilters()

    def configureDatasetTimeZone(self, exportType):
        """Checks whether or not the currently exported file requires a time zone to be assigned to its metadata.

        Certain types of exports are excluded as they do not require time zones in the export process.
        Calls the time zone selection dialog if no time zone is found.
        Returns:
            None if the time zone selection dialog was closed without making a selection
            1 if the exporting file type does not require a time zone
            +/-##:## from UTC time zones if the user set a time zone
        exportType --- str; type of file being exported, originates from 'MainToolbar.py''s export dropdown
        """
        excludeTimezones = ["geoprecision"]  # There's probably a better place for this
        if exportType not in excludeTimezones:
            meta = self.tableData.getDatasetMetadata()
            if meta.getField("time_zone") is None:
                return TimeZoneConfigure(self.parent).display()
        return 1

    def getMetadata(self):
        return self.tableData.getDatasetMetadata().formatted()
        
    def exportData(self, exportPath, exportType):
        Exporter = get_exporter(exportType)
        metadata = self.tableData.getDatasetMetadata()
        
        if Exporter is None:
            raise KeyError(f"{exportType} not valid")

        if Exporter.REQUIRE_TIMEZONE:
            configureTimeRes = self.configureDatasetTimeZone(exportType)
            if configureTimeRes is None:
                return
            elif configureTimeRes == 1:
                pass
            else:  # If not 1, it meant that a time zone was returned
                metadata.setField("time_zone", configureTimeRes)

        if Exporter.REQUIRE_TRUE_DEPTH and not metadata._trueDepths:
            if metadata.getDepthMap() is {}:

                if self.renameDepths() is None:
                    # If user closed out of the renaming depth dialog, stop exporting
                    return
        if Exporter.REQUIRED_METADATA != {}:
            
            # check what exists already in the metadata and set as default
            required = Exporter.REQUIRED_METADATA
            filled_required = {}
            for key, value in required.items():
                if metadata.getField(key) is not None:
                    filled_required[key] = (value[0], value[1], value[2], metadata.getField(key))
                else:
                    filled_required[key] = value
            
            d = MetadataInputDialog(self.parent, filled_required).display()
            # If user closed out of the metadata dialog, stop exporting
            if d is None:
                return
            else:
                for key, value in d.items():
                    metadata.setField(key, value)

        try:
            exporter = Exporter(data=self.tableData.getExportableDataframe(),
                                meta=metadata)
            
            exporter.export(pathObj=Path(exportPath))
            self.exportLogData(exportPath)

        except OSError as err:
            tk.messagebox.showerror(title="File Export Error", message=err)
        except Exception as err:
            tk.messagebox.showerror(title="File Export Error", message=f"{err}\ncheck the python console for more information")
        else:
            tk.messagebox.showinfo(title="Save Complete", message="Successfully exported data!")

    def exportLogData(self, filepath):
        logPathObj = Path(filepath)
        filepath = f"{filepath}.log" if logPathObj.suffix == "" else f"{logPathObj.parent.joinpath(logPathObj.stem)}.log"
        try:
            with open(filepath, "w") as fp:
                fp.write(self.actionLogger.getMetadata())
                fp.write(self.actionLogger.getLog())
        except OSError as err:
            tk.messagebox.showerror(title="Log File Save Error", message=err)
        else:
            tk.messagebox.showinfo(title="Saved Log", message="Successfully saved log file!")

    def importLog(self, logPath):
        def checkMetadata(logMeta):
            prog_ver, original_name, unique_times, unique_depths = self.actionLogger.getAccessibleMetadata()
            if not logMeta["tempcf_version"] == prog_ver:
                tk.messagebox.showinfo(title="Info Mismatch", message="The current version of tempcf does not match the version used to generate this log file.")
            if not logMeta["original_file"] == original_name:
                tk.messagebox.showinfo(title="Info Mismatch", message="The current dataset file name does not match the file name used to generate this log file.")
            if not logMeta["unique_times"] == str(unique_times):
                tk.messagebox.showinfo(title="Info Mismatch", message="The number of timestamps in the current dataset does not match the number of timestamps indicated in the log file.")
            if not logMeta["unique_depths"] == str(unique_depths):
                tk.messagebox.showinfo(title="Info Mismatch", message="The number of depths in the current dataset does not match the number of depths indicated in the log file.")
        try:
            logMetadata, logChanges = lp.parseLog(logPath)
        except RuntimeError as err:
            tk.messagebox.showerror(title="Error", message=f"Failed to parse log file: \n{err}")
            return
        except ValueError as err:
            tk.messagebox.showerror(title="Error", message=err)
            return
        checkMetadata(logMetadata)
        try:
            self.tableData.selectableDataframe = lp.applyLogChanges(logChanges, self.tableData.selectableDataframe)
            self.redrawPoints()
        except Exception as err:
            tk.messagebox.showerror(title="Error", message=err)
        else:
            tk.messagebox.showinfo(title="Applied Log", message="Successfully applied log file to the current dataset!")

    def loadedData(self, orig, select):
        self.actionLogger.setDataframeInfo(orig)
        self.graphView.createGraph(orig, select, self.tableData.getDepthMask())
        try:
            self.filterControl.initFilters()
        except AssertionError as err:
            tk.messagebox.showerror(title="Error", message=err)

    def loadedDepths(self, depths):
        self.options.loadDepths(depths)
        
        # Bind depth toggles to keys
        for i, state in enumerate(self.options.depthStates):

            def toggleDepth(event, state=state, depth=depths[i]):
                state.set(not state.get())
                self.toggleDepth(depth)
            if (i <= 8):
                self.parent.bind(f"{i+1}", toggleDepth)
            if (9 < i <= 17):
                self.parent.bind(f"<Control-{i-8}>", toggleDepth)
            else:
                pass

        self.parent.bind("`", lambda event: self.options.toggleNoDepths())
        self.parent.bind("<Control-`>", lambda event: self.options.toggleAllDepths())
        
    def toggleDepth(self, depth):
        self.tableData.toggleDepth(depth)

    def toggleAllDepths(self):
        self.tableData.toggleAllDepths()

    def toggleNoDepths(self):
        self.tableData.toggleNoDepths()

    def renameDepths(self):
        depthRes = DepthConfigure(self.parent).display(self.tableData.getDepths())

        if depthRes is None:
            return depthRes
        else:
            meta = self.tableData.getDatasetMetadata()
            meta.setDepthMap({oldCol: float(newCol.get()) for oldCol, newCol in depthRes.items()})  # Make a new dict with the .get() on the StringVars
            # re-label toolbar
            for i, originalDepth in enumerate(depthRes):
                self.options.depths_dropdown.entryconfig(i, label=depthRes[originalDepth].get())
            
            return depthRes

    def loadFilters(self, filters):
        self.options.loadFilters(filters)

    def addFilter(self, filter):
        self.filterControl.addFilter(filter)
        self.filterView.addFilter(filter)

    def removeFilter(self, index):
        self.filterControl.removeFilter(index)

    def applyFilter(self, filterId):
        activeFilter = self.filterControl.getFilter(filterId)
        self.tableData.applyFilter(activeFilter.getFunction(), activeFilter.getUserParams())
        self.filterView.postFilterAction(self.tableData.filter.get().sum())

    def setSelectedIndex(self, indices):
        self.tabledata.updateSelection(indices)

    def clearFilterList(self):
        self.filterView.clearList()

    def redrawPoints(self, empty=None):
        filtered = self.tableData.filter.get()
        selectable = self.tableData.selectableDataframe
        depths = self.tableData.getDepthMask()
        select_i = self.tableData.select_i.get()
        self.graphView.drawSelectable(selectable, depths, select_i, filtered)

    def updateLassoSelection(self, data):
        trueSelection = self.tableData.updateSelection(data)
        if len(trueSelection) > 0:
            self.filterView.activateSelectionButtons()
        else:
            self.filterView.deactivateSelectionButtons()

    def changedData(self):
        self.redrawPoints()

    def logAction(self, affectedRows, newValue):
        """Records an action affected selected data (replace with value or np.nan).

        affectedRows --- list of 3 series of time, depth, temperature
        newValue --- the new temperature value that is replacing the old temperature value at all of the affected rows
        """
        affectedRows = [row.astype(str).tolist() for row in affectedRows]
        refSeries = affectedRows[0]
        for index, val in enumerate(refSeries):
            # First argument is the time, second is the depth, third is the old temperature value, fourth is the new value
            self.actionLogger.log(affectedRows[0][index], affectedRows[1][index], affectedRows[2][index], newValue)

    def selectFilteredData(self):
        self.graphView.selectFilteredData(self.tableData.filter.get())

    def deleteSelectedData(self):
        self.tableData.replace(self.tableData.select_i.get())

    def replaceSelectedData(self, newValue):
        self.tableData.replace(self.tableData.select_i.get(), newValue)

    def updateTitle(self, title="Permafrost Data - Temperature Cleaning and Filtering"):
        self.parent.title(title)


def sc_quit(quitFunction):
    quitFunction()


def main():
    logger.info("Starting TempCF")
    root = tk.Tk()
    root.iconbitmap(resourcePath("assets/permafrostnet_logo.ico"))
    app = MainWindow(root)
    app.pack()
    root.bind("<Control-w>", lambda ev: sc_quit(app.options.closeFile))
    root.bind("<Control-q>", lambda ev: app.destroy())
    root.title("Permafrost Data - Temperature Cleaning and Filtering")
    root.mainloop()


if __name__ == "__main__":
    main()
