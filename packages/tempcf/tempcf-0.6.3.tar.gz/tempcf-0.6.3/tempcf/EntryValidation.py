class Validator:
    """ Validator class for validating the data type of TKinter entry fields 
    type : 
    sendError : function that takes a single argument to send error message to the user
    """

    def __init__(self, type:str):
        self._type = type

    def validate(self, input:str):
        validator = self.get_validator(self._type)
        result = validator(input)
        return result

    def get_validator(self, type):
        if type in ["int", int]:
            return self._intCheck
        elif type in ["float", float]:
            return self._floatCheck
        else:
            return self._strCheck

    def _strCheck(self, value):
        return True

    def _intCheck(self, value):
        if value in ["", "-", "."]:
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
            
    def _floatCheck(self, value):
        if value in ["", "-", "."]:
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
