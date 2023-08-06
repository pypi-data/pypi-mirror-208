# From https://gist.github.com/ajfigueroa/c2af555630d1db3efb5178ece728b017
class Observable:
    def __init__(self, initialvalue=None):
        self.data = initialvalue
        self.callbacks = {}

    def setCallback(self, fname, func):
        self.callbacks[fname] = func
        
    def deleteCallback(self, fname):
        del self.callbacks[fname]
    
    def _docallbacks(self):
        for name in self.callbacks:
            func = self.callbacks[name]
            func(self.data)

    def set(self, data):
        self.data = data
        self._docallbacks()

    def get(self):
        return self.data

    def unset(self):
        self.data = None