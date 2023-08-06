from inspect import getdoc, getmembers, isfunction, signature, _empty

import tempcf.Filters as filters

from tempcf.Observable import Observable
from tempcf.FilterContainer import FilterContainer


class FilterControl():
    FILTER_DEFAULT_ARGUMENTS = ["values", "timestamps", "depths"]

    def __init__(self):
        self._filterCounter = 0
        self._filters = []
        self._configuredFilters = []
        self.filterCntrlObservable = Observable()
    
    def checkDefinitions(self, args):
        """Validates that the functions in Filters.py are properly formed.
Asserts that the name of each argument without a default value is found within FILTER_DEFAULT_ARGUMENTS.
        args --- parameters of a filter function
        """
        try:
            for parameter in args:
                if args[parameter].annotation == _empty: # If it was not assigned a default value, it should be one of the default argument names
                    assert parameter in self.FILTER_DEFAULT_ARGUMENTS
        except AssertionError:
            raise AssertionError(f"A defined filter contains an unknown non-default parameter name ({parameter}). \nAccepted non-defaulting parameter names are:\n{', '.join(self.FILTER_DEFAULT_ARGUMENTS)}. \nPlease correct the definitions and try again.")
    
    def getDefaultFilterArgs(self, args):
        """Returns a list of the arguments from a Filters.py function that is assigned a default value.
        
        The parameter name, type, and default value are collected and returned.
        args --- dictionary of parameters for a filter function
        """
        defaults = []
        for parameter in args:
            if args[parameter].annotation != _empty:
                defaults.append((parameter, args[parameter].annotation, args[parameter].default))
        return defaults

    def initFilters(self):
        for f in getmembers(filters, isfunction):
            filter_params = signature(f[1]).parameters
            self.checkDefinitions(filter_params)
            self._filters.append(FilterContainer(f[0], f[1], self.getDefaultFilterArgs(filter_params), getdoc(f[1])))
        self.filterCntrlObservable.callbacks["loadFilters"](self._filters)
    
    def addFilter(self, filter):
        filter.setIdentifier(self._filterCounter)
        self._filterCounter += 1
        self._configuredFilters.append(filter)
    
    def removeFilter(self, index):
        del self._configuredFilters[index]
    
    def getFilter(self, id):
        return next(filter(lambda f: f.getIdentifier() == id, self._configuredFilters))
    
    def clearFilters(self):
        self._filters = []
        self.filterCntrlObservable.callbacks["clearFilters"]()
        
