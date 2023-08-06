from abc import ABC, abstractmethod
from typing import Type, Any

from tsp import TSP
import tempcf.FileTypes as ft


class AbstractExporter(ABC):

    REQUIRE_TIMEZONE = False
    REQUIRE_TRUE_DEPTH = False
    REQUIRED_METADATA: "dict[str, tuple[str, str, Any, Any]]" = {}

    @abstractmethod
    def __init__(self, data, meta, **kwargs):
        pass

    @abstractmethod
    def export(self, pathObj):
        pass

    @property
    def required_metadata(self) -> "dict[str, tuple[str, str, Any, Any]]":
        """ Returns a dictionary of metadata attributes that are required for the exporter.

        Returns
        -------
        dict[str, tuple[str, str, Any, Any]]
            a dictionary whose key is the metadata attribute name, and whose value is a tuple of:
            1 (str) How variable should be displayed
            2 (str) A description of the attribute
            3 (Any) The variable type of the attribute
            4 (Any) The default value of the attribute

        """
        return self.REQUIRED_METADATA


def get_exporter(transformType:str) -> Type[AbstractExporter]:
    if transformType == ft.GTNP:
        return ExportGtnp
    elif transformType == ft.NTGS:
        return ExportNtgs
    elif transformType == ft.FG2:
        return ExportFg2
    elif transformType == ft.GP5W:
        return ExportGp5w
    else:
        raise KeyError(f"Exporter '{transformType}' not found.")


class ExportGtnp(AbstractExporter):
    REQUIRE_TRUE_DEPTH = True

    def __init__(self, data, meta):
        self.t = TSP.from_tidy_format(times=data['time'],
                                      depths=data['depth'],
                                      values=data["temperature"].values)

    def export(self, pathObj):
        self.t.to_gtnp(pathObj)


class ExportNtgs(AbstractExporter):
    REQUIRE_TRUE_DEPTH = True
    REQUIRED_METADATA = {"latitude" : ("latitude", "Latitude of measurements", float, None),
                         "longitude" : ("longitude", "Longitude of measurements", float, None),
                         "project" : ("project_name", "Name of project", str, ""),
                         "platform_id" : ("site_id", "Name of location where data were collected", str, "")}

    def __init__(self, data, meta):
        self.t = TSP.from_tidy_format(times=data['time'],
                                      depths=data['depth'],
                                      values=data["temperature"].values)
        self.meta = meta

    def export(self, pathObj):
        lat = self.meta.getLatitude() if self.meta.getLatitude() is not None else None
        lon = self.meta.getLongitude() if self.meta.getLongitude() is not None else None
        project_name = self.meta.getProject() if self.meta.getProject() is not None else None
        site_id = self.meta.getPlatformId() if self.meta.getPlatformId() is not None else None

        self.t.to_ntgs(pathObj,
                       project_name=project_name,
                       site_id=site_id,
                       latitude=lat, longitude=lon)


class ExportNetCDF(AbstractExporter):
    def __init__(self):
        pass

    def netCDFTime(self, timestamp):
        # Add in the time zone, then convert that to unaware UTC time
        return timestamp.replace(tzinfo=self._meta.getField("time_zone")).tz_convert(None)

    def export(self,pathObj):
        pass


class ExportGeoPrecision(AbstractExporter):

    TIME_FORMAT = "%d.%m.%Y %H:%M:%S"

    def __init__(self, data, meta, geoprecisionType):
        self._data = data
        self._meta = meta
        self._gpType = geoprecisionType
        self.t = TSP.from_tidy_format(times=data['time'],
                                      depths=data['depth'],
                                      values=data["temperature"].values)

    def geoprecisionTime(self, timestamp):
        return timestamp.strftime(self.TIME_FORMAT)

    def make_header(self, meta) -> 'list[str]':
        raise NotImplementedError("Implement this in child class")
    
    def columns(self, n:int):
        raise NotImplementedError("Implement this in child class")
    
    def index(self):
        raise NotImplementedError("Implement this in child class")
    
    def export(self, pathObj):
        df = self.t.wide
        df.columns = self.columns(len(df.columns))
        df.iloc[:,0] = df.iloc[:,0].dt.strftime(self.TIME_FORMAT)
        df.index = range(len(df))
        df.index.name = self.index()
        df = df.reset_index()
        df.index += 1  # GeoPrecision files' "No" columns start at 1 instead of zero.

        header = "".join(self.make_header(self._meta))

        try:
            with open(f"{str(pathObj)}", 'w') as fp:
                fp.write(header + df.to_csv(encoding="utf-8", float_format="%.4f", line_terminator="\n", index=False))
        except OSError:
            raise OSError(f"The file was unable to save at:\n{str(pathObj)}\nThe file may be open in another location.")


class ExportGp5w(ExportGeoPrecision):
    
    REQUIRED_METADATA = {"logger_serial_number": ("serial_number", 'serial number of geoprecision logger', str, "")}

    def __init__(self, data, meta):
        super().__init__(data, meta, "5W")

    def make_header(self, meta) -> 'list[str]':
        logger_serial_number = meta.getField("logger_serial_number")
        logger_type = "???"
        firmware_version = "???"
        header = [f"Logger: #{logger_serial_number} '{logger_type}' - USP_EXP2 - (CGI) Expander for GP5W - (V{firmware_version}, Jan XX YYYY)\n"]
        
        return header

    def columns(self, n):
        return ["Time"] + [f"#{n}:oC" for n in range(1, n)]

    def index(self):
        return "No"


class ExportFg2(ExportGeoPrecision):

    REQUIRED_METADATA = {"logger_serial_number": ("serial_number", "serial number of geoprecision logger", str, "")}

    def __init__(self, data, meta):
        super().__init__(data, meta, "FG2")

    def make_header(self, meta) -> 'list[str]':
        logger_serial_number = meta.getField("logger_serial_number")
        firmware_version = "???"
        header = [f"<FG2 'FG2-SHELL V{firmware_version}' (Apr  X YYYY) NOW(UTC):21.10.2019 19:16:43>\n",
                  f"<LOGGER: ${logger_serial_number}>\n"]

        return header

    def columns(self, n):
        return ["TIME"] + [f"#{n}(oC)" for n in range(1, n)]

    def index(self):
        return "NO"
