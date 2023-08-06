class FilterContainer():
    def __init__(self, name, function, params, helptext=""):
        self._name = name
        self._function = function
        self._params = params
        self._helptext = helptext
        self._identifier = None
        self._uinput_params = {}
    
    def getName(self):
        return self._name
        
    def getParams(self):
        return self._params
        
    # def setParams(self, newParams):
        # self._params = newParams
    
    def setIdentifier(self, id):
        # Identifier is to determine what was removed from the GUI's list and the corresponding internal list of filters being managed
        self._identifier = id
        
    def getIdentifier(self):
        return self._identifier
    
    def getUserParams(self):
        return self._uinput_params
        
    def setUserParams(self, userParams):
        for key, value in userParams.items():
            self._uinput_params[key] = value
    
    def getFunction(self):
        return self._function
    
    def getHelpText(self):  
        return self._helptext