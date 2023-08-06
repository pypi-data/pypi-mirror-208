from abc import ABC, abstractmethod
import re
import tsp.readers as tspr

from tempcf.DatasetMetadata import DatasetMetadata
import tempcf.FileTypes as ft


class ImportType():
    def __init__(self, filepath, importType):
        self._importer = self._createImporter(filepath, importType)

    def _createImporter(self, filepath, importType):
        if importType == ft.NTGS:
            return ImportNtgs(filepath)
        elif importType == "netcdf":
            return None
        elif importType == ft.GEOPREC:
            return ImportGeoPrecision(filepath)
        elif importType == "database":
            return None
        elif importType == ft.HOBO:
            return ImportHOBO(filepath)
        elif importType == ft.GTNP:
            return ImportGtnp(filepath)
        elif importType == ft.RBR:
            return ImportRBR(filepath)
        else:
            pass

    def importData(self):
        return self._importer.importData()


class AbstractImporter(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def importData(self):
        pass


# util
def getColumnMode(series):
    mode = series.mode()
    return mode[0] if not mode.empty else ""


class ImportGeoPrecision(AbstractImporter):
    def __init__(self, filepath):
        self._filepath = filepath

    def importData(self):
        t = tspr.read_geoprecision(self._filepath)
        original = t.long.rename(columns={"temperature_in_ground":"temperature"})

        meta = DatasetMetadata(self._filepath)
        meta._metaFields.update(t.metadata)
        return original, meta


class ImportRBR(AbstractImporter):

    def __init__(self, filepath):
        self._filepath = filepath

    def importData(self):
        t = tspr.read_rbr(self._filepath)
        original = t.long.rename(columns={"temperature_in_ground": "temperature"})
        meta = DatasetMetadata(self._filepath)

        if t.utc_offset:
            meta.setField("utc_offset", t.utc_offset)

        meta._metaFields.update(t.metadata)
        return original, meta
        
class ImportHOBO(AbstractImporter):

    def __init__(self, filepath):
        self._filepath = filepath

    def importData(self):
        t = tspr.read_hoboware(self._filepath)
        original = t.long.rename(columns={"temperature_in_ground": "temperature"})
        meta = DatasetMetadata(self._filepath)

        if t.utc_offset:
            meta.setField("utc_offset", t.utc_offset)
        # meta.setField("HOBO_meta_header", self._dataHandler.META)  # TODO: get metadata from t.metadata

        # self.set_tz_meta(meta)  # TODO: set time zone if available
        meta._metaFields.update(t.metadata)
        return original, meta

    def set_tz_meta(self, meta):
        pattern = re.compile(r"([+-]\d{2})(\d{2})")
        if pattern.match(self._dataHandler.META.get("tz_offset")):
            tz = pattern.sub(r"\1:\2", self._dataHandler.META["tz_offset"])
            meta.setField("time_zone", tz)


class ImportNtgs(AbstractImporter):

    def __init__(self, filepath):
        self._filepath = filepath

    def importData(self):
        t = tspr.read_ntgs(self._filepath)
        original = t.long.rename(columns={"temperature_in_ground": "temperature"})
        meta = DatasetMetadata(self._filepath)

        meta.setLatitude(t.latitude)
        meta.setLongitude(t.longitude)
        meta.setPlatformId(t.site_id)
        meta.setProject(t.metadata["project_name"])

        meta.setDepthMap({str(d) : d for d in t.depths})
        meta._metaFields.update(t.metadata)
        return original, meta


class ImportGtnp(AbstractImporter):

    def __init__(self, filepath):
        self._filepath = filepath

    def importData(self):
        t = tspr.read_gtnp(self._filepath)
        original = t.long.rename(columns={"temperature_in_ground": "temperature"})
        meta = DatasetMetadata(self._filepath)

        meta.setLatitude(t.latitude)
        meta.setLongitude(t.longitude)
        meta._metaFields.update(t.metadata)
        return original, meta
