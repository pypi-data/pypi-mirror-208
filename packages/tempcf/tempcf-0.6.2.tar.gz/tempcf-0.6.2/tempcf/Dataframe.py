from inspect import signature
import numpy as np
import tkinter as tk
from tsp import TSP

from tempcf.ImportType import ImportType
from tempcf.Observable import Observable
from tempcf.DatasetMetadata import DatasetMetadata


class Dataframe():
    def __init__(self):
        self._activeFile = None
        self._originalDataframe = None  # Does not change
        self._datasetMetadata = DatasetMetadata(self._activeFile)
        self.selectableDataframe = None  # Changes when filtering or doing other operations
        self._importType = "wide"
        self._depths = []
        self.dataframeObservable = Observable()
        self.select_i = Observable(np.nonzero(0)[0])
        self.filter = Observable()
        self.visibleDepths = Observable(list())
        self.depthMask = Observable(np.ones(0, dtype=bool))

    def toTsp(self):
        if self.selectableDataframe is None:
            raise ValueError("No data in selectable dataframe.")
        else:
            t = TSP.from_tidy_format(times=self.selectableDataframe['time'],
                                     depths=self.selectableDataframe['depth'],
                                     values=self.selectableDataframe["temperature"].values)

        return t

    def resetSelection(self):
        """ Set selection to no data points without triggering callbacks."""
        self.select_i.data = np.nonzero(0)[0]

    def getActiveFile(self):
        return self._activeFile

    def setFile(self, filepath):
        self._activeFile = filepath
        self.loadData()
        check_data(self)

    def setDataType(self, dataType):
        self._importType = dataType

    def getDepths(self):
        return self._depths

    def getTrueDepths(self):
        if self.selectableDataframe is None:
            raise RuntimeError("Dataframe not loaded yet")
        
        if self.getDatasetMetadata()._trueDepths:
            depth_map = self.getDatasetMetadata().getDepthMap()
            return self.selectableDataframe["depth"].astype('string').map(depth_map)
        else:
            raise RuntimeError("True depths not set")

    def getDepthMask(self):
        return self.depthMask.get()

    def replace(self, indices, value=np.nan):
        """Replaces values at given indices.

        Also collects the values that were replaced to be logged.
        indices --- list of indices to select in the dataframe [0, ..., n]
        value --- numeric value that will replace the original values of the indices (default: np.nan)
        """
        affectedRows = [
            self.selectableDataframe.loc[indices, "time"],
            self.selectableDataframe.loc[indices, "depth"],
            self.selectableDataframe.loc[indices, "temperature"]
        ]
        self.selectableDataframe.loc[indices, "temperature"] = value
        self.dataframeObservable.callbacks["logAction"](affectedRows, value)
        self.dataframeObservable.callbacks["changedData"]()

    def applyFilter(self, filterFunction, filterArgs):
        result = filterHandler(filterFunction, self.selectableDataframe, filterArgs)
        self.filter.set(result)

    def loadData(self):
        """Imports and shapes data into internal long format.

        Obtains the original dataframe per the type of import passed, along with the dataset's metadata.
        Prepares the depths and sets values in preparation for toggling or selection.
        """
        Importer = ImportType(self._activeFile, self._importType)
        self._originalDataframe, self._datasetMetadata = Importer.importData()
        self.selectableDataframe = self._originalDataframe.copy()
        self._depths = self._originalDataframe["depth"].unique()
        self.__initializeVisibleDepths(self._depths, self._originalDataframe["depth"])
        self.filter.data = np.zeros(len(self.selectableDataframe), dtype=bool)
        self.dataframeObservable.callbacks["loadedData"](self._originalDataframe, self.selectableDataframe)
        self.dataframeObservable.callbacks["loadedDepths"](self._depths)

    def __initializeVisibleDepths(self, depths, depthColumn):
        self.visibleDepths.data = np.array(depths)
        self.depthMask.data = np.ones_like(depthColumn, dtype=bool)

    def updateSelection(self, indices):
        trueSelection = indices[self.depthMask.get()[indices]]
        self.select_i.set(trueSelection)
        if len(self.select_i.get()):
            print(f"Selected {len(self.select_i.get())} points")
        return trueSelection

    def refreshSelection(self):
        self.updateSelection(self.select_i.get())

    def toggleAllDepths(self):
        self.visibleDepths.set(self._depths)
        self.depthMask.data = np.ones_like(self._originalDataframe["depth"], dtype=bool)
        self.refreshSelection()
        self.notifyVisibleDepthsChanged()

    def toggleNoDepths(self):
        self.visibleDepths.set([])
        self.depthMask.data = np.zeros_like(self._originalDataframe["depth"], dtype=bool)
        self.refreshSelection()
        self.notifyVisibleDepthsChanged()

    def toggleDepth(self, depth):
        """Redraws the graph with the selected depths.

        depth --- float value, depth whose visibility will be toggled on or off. This value originates from this class's loadData function, where it then passes the depths along to the toolbar for toggling
        """
        visible = self.visibleDepths.get()
        if depth in visible:
            self.visibleDepths.set(visible[visible != depth])

        elif depth not in visible and depth in self.getDepths():
            self.visibleDepths.set(np.append(visible, depth))

        else:
            raise ValueError(f"depth {depth} is not valid")

        isDepth = np.array(self.selectableDataframe["depth"] == depth, dtype=bool)
        self.depthMask.get()[isDepth] = np.logical_not(self.depthMask.get()[isDepth])
        self.depthMask.set(self.depthMask.get())
        self.refreshSelection()
        self.notifyVisibleDepthsChanged()
        
    def notifyVisibleDepthsChanged(self):
        if self.getDatasetMetadata()._trueDepths:
            d = self.visibleDepths.get()
        else:
            d = self.visibleDepths.get()
        print(f"visible depths changed to: {d}")

    def getExportableDataframe(self):
        """Returns a copy of the modifiable dataframe to be used in exporting."""
        df = self.selectableDataframe.copy()
        
        try:
            df["depth"] = self.getTrueDepths()
        except RuntimeError:  # True depths not set
            pass

        return df

    def getDatasetMetadata(self):
        return self._datasetMetadata


def filterHandler(filterFunction, df, filterKwargs):

    """
    Applies a filter on a dataframe, handles the extraction of the necessary
    data from the data frame
    """

    f = signature(filterFunction)
    depths = df["depth"]
    result = np.zeros_like(depths, dtype=bool)

    for d in depths.unique():
        i = (depths == d)

        params = dict()
        params["values"] = df.loc[i, "temperature"] if "values" in f.parameters else None
        params["depths"] = df.loc[i, "depth"] if "depths" in f.parameters else None
        params["timestamps"] = df.loc[i, "time"] if "timestamps" in f.parameters else None

        args = {k: v for k, v in params.items() if v is not None}

        result[i] = filterFunction(**args, **filterKwargs)

    return result


def check_data(d: Dataframe):
    """ Check incoming data. Throw popups if problems are found. """
    if d._originalDataframe.duplicated(subset=['time','depth']).any():
        tk.messagebox.showerror("Warning", "Duplicate timestamps found in data. Exporting may not be possible.\
                                \nSee the console log for more information")