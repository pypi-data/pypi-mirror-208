import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path

from tempcf.Observable import Observable


class GraphView(tk.Frame):
    PLOT_PARAMETERS = {'unselected_unflagged': {'s': 2,'c': "#535379"},
                       'selected_unflagged':   {'s': 4,'c': "#0000cc"},
                       'unselected_flagged':   {'s': 2,'c': "#a32929"},
                       'selected_flagged':     {'s': 4,'c': "#cc0000"}}

    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.parent = parent
        self.figure = None
        self.toolbar = None
        self.canvas = None
        self.frame.pack()
        self.select_i = Observable(np.nonzero(0)[0])

        self.selectedshow = list()

    def resetSelection(self):
        """ Set selection to no data points without triggering callbacks."""
        self.select_i.data = np.nonzero(0)[0]

    def onSelect(self, data):
        """ Update the indices of selected points.

        data --- the vertices of the path obtained from LassoSelector
        """
        path = Path(data)
        self.select_i.set(np.nonzero(path.contains_points(self.xys))[0])

    def selectFilteredData(self, indices):
        """ Select all data for which the active filter is True.

        indices --- boolean array created by a filter"""
        self.select_i.set(np.where(indices)[0])
        self.canvas.draw_idle()

    def createGraph(self, original, selectable, depths):
        """ Create graphing canvas from scratch and draw data
        original --- unmodified dataframe (m x n)
        selectable --- dataframe that will be edited (m x n)
        depths --- boolean array of length m corresponding to which depths are active
        """
        if self.figure:
            self.figure.clear()
        if self.toolbar:
            self.toolbar.destroy()

        self.figure = Figure(figsize=(10,8))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.parent)
        self.drawOriginal(original, self.ax)
        self.drawSelectable(selectable, depths, self.select_i.get(), None)
        self.lasso = LassoSelector(self.ax, onselect=self.onSelect)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.toolbar.update()
        self.canvas.draw()

    def closeGraph(self):
        """ Remove graph object from canvas """
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.resetSelection()

    def drawOriginal(self, original, depths):
        """ Add temperature time-series line graph of unmodified dataset to canvas."""
        if hasattr(self, "originalplot"):
            del self.originalplot

        # TODO: don't make groupby transformation on-the-fly
        widedata = original.groupby(['time', 'depth'])['temperature'].aggregate('mean').unstack()

        self.originalplot = self.ax.plot(widedata.index.values, widedata.values, '#5e5e5e', linewidth=0.1, zorder=1)

    def removeDataFromGraph(self):
        """ remove series objects from matplotlib canvas if they exist"""
        if hasattr(self, "selectedplot"):
            self.selectedplot.remove()

        if hasattr(self, "selectedshow"):
            while len(self.selectedshow) > 0:
                S = self.selectedshow.pop()
                S.remove() if S else None

    def drawSelectable(self, selectable, depths, select_i, filtered):
        """ Draw data points.

        Points are drawn with different colours and sizes depending on whether they are filtered or selected.

        selectable --- a (m x n) dataframe with columns (time, temperature, depth)
        depths --- boolean array of length m corresponding to which depths are toggled on
        select_i --- list of integers corresponding to the indices of the data points that have been selected.
        filtered --- boolean array of length  m identifying which indicies of the data frame have been identified by a filter
        """
        self.removeDataFromGraph()

        self.selectedplot = self.ax.scatter(selectable['time'],
                                            selectable['temperature'],
                                            s=0)  # these don't have markers but are used to get the index
        self.xys = self.selectedplot.get_offsets()

        selected = np.zeros(selectable.shape[0], dtype=bool)
        selected[select_i] = True

        if filtered is None:
            filtered = np.zeros_like(selected, dtype=bool)

        self.selectedshow = list()

        # Adding different colours as different series is much faster than passing an array of plot properties
        self.selectedshow.append(self.__drawPointsWithProperties(selectable,
                                                                 np.logical_not(selected) & np.logical_not(filtered),
                                                                 'unselected_unflagged', depths))
        self.selectedshow.append(self.__drawPointsWithProperties(selectable, selected & np.logical_not(filtered),
                                                                 'selected_unflagged', depths))
        self.selectedshow.append(self.__drawPointsWithProperties(selectable, np.logical_not(selected) & filtered,
                                                                 'unselected_flagged', depths))
        self.selectedshow.append(self.__drawPointsWithProperties(selectable, selected & filtered,
                                                                 'selected_flagged', depths))

        # Preserve zoom settings after making a lasso selection
        self.ax.set_xlim(self.ax.get_xlim())
        self.ax.set_ylim(self.ax.get_ylim())
        self.canvas.draw_idle()

    def __drawPointsWithProperties(self, data, selected, properties, depths):
        """ Add a points data series to the canvas.

        data --- a (m x n) dataframe with columns (time, temperature, depth)
        selected --- boolean array of length m corresponding to which indices of the data have been selected.
        properties --- dictionary of matplotlib plotting parameters
        depths --- boolean array of length m corresponding to which depths are toggled on
        """
        params = self.PLOT_PARAMETERS[properties]
        plotTrue = selected & depths
        if np.any(plotTrue):
            y = data.loc[plotTrue, 'temperature']
            if not np.all(np.isnan(y)):
                return self.ax.scatter(data.loc[plotTrue, 'time'],
                                       y, zorder=2, **params)
