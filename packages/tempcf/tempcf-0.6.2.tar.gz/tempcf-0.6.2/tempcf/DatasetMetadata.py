from typing import Union
from pprint import pformat
import re
import codecs

class DatasetMetadata():
    def __init__(self, filepath):
        self._filepath = filepath
        self._metaFields = {'filepath': filepath}
        self._trueDepths = False
        self._depth_map = {}
        
    def setField(self, metaCol, metaColValue):
        self._metaFields[metaCol] = metaColValue
 
    def getField(self, metaKey):
        try:
            return self._metaFields[metaKey]
        except KeyError:
            return None
    
    def getAllFields(self):
        return self._metaFields.items()
    
    def setDepthMap(self, depths: "dict[Union[str,int,float], float]"):
        if not isinstance(depths, dict):
            raise ValueError("Depth map must be a dictionary")
        
        self._trueDepths = True
        self._depth_map = depths
        
    def getDepthMap(self) -> "dict[Union[str,int,float], float]":
        return self._depth_map
    
    def getLatitude(self):
        return self.getField("latitude")
        
    def setLatitude(self, latitude):
        self.setField("latitude", latitude)
    
    def getLongitude(self):
        return self.getField("longitude")
        
    def setLongitude(self, longitude):
        self.setField("longitude", longitude)
    
    def getProject(self):
        return self.getField("project")
        
    def setProject(self, project):
        self.setField("project", project)
    
    def getPlatformId(self):
        return self.getField("platform_id")
        
    def setPlatformId(self, platform_id):
        self.setField("platform_id", platform_id)

    def formatted(self):
        text = pformat(self._metaFields)
        return decode_escapes(text)


ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)
