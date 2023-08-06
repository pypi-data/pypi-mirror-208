class ActionLogger():
    def __init__(self, progVer):
        self._logState = []
        self._version = progVer
        self._associatedRawData = None
        self._uniqueTimes = None
        self._uniqueDepths = None
	
    def setFile(self, rawData):
        self._associatedRawData = rawData
        self._logState = []
    
    def setDataframeInfo(self, df):
        self._uniqueTimes = df["time"].nunique()
        self._uniqueDepths = df["depth"].nunique()
    
    def getAccessibleMetadata(self):
        return self._version, self._associatedRawData, self._uniqueTimes, self._uniqueDepths
    
    def getMetadata(self):
        import datetime
        return (
            f"#Log Creation (UTC): {str(datetime.datetime.now(datetime.timezone.utc))}\n"
            f"#tempcf Version: {self._version}\n"
            f"#Original File Name: {self._associatedRawData}\n"
            f"#Unique Timestamps in Original File: {self._uniqueTimes}\n"
            f"#Unique Depths In Original File: {self._uniqueDepths}\n"
            f"original_date,original_depth,original_value,new_value\n"
        )

    def log(self, date, depth, original, new):
        self._logState.append(f"{date},{depth},{original},{new}")

    def getLog(self):
        return "\n".join(self._logState)
