"""
input: a time-series as 
returns: a numpy boolean array the same length as time series
underscore prefix ('_') = common interface
without double underscore
"""
import numpy as np
import pandas as pd

from typing import Union
from datetime import datetime


def min_filter(values,
               lower: float = -50):
    """Flags data less than or equal to a lower bound

    Parameters
    ----------
    lower : float, optional
        The lower bound, by default -50

    Returns
    -------
    boolean array
        True when the measured temperature value is below the lower bound
    """
    result = values <= lower
    assert len(values) == len(result)
    return result


def max_filter(values,
               upper: float = 35):
    """Flags data less than or equal to an upper bound

    Parameters
    ----------
    upper : float, optional
        The upper bound, by default 35

    Returns
    -------
    boolean array
        True when the measured temperature value is above the upper bound
    """
    result = values >= upper
    assert len(values) == len(result)
    return result


def range_filter(values,
                 lower: float = -50,
                 upper: float = 35):
    """
    Flags data outside of a specified range
    """
    lower_flag = min_filter(values, lower)
    upper_flag = max_filter(values, upper)
    flag = lower_flag | upper_flag
   
    return flag


def time_filter(values, timestamps,
                start: "Union[str, datetime,None]" = None,
                end: "Union[str, datetime,None]" = None,
                invert: bool = False,
                timeformat: str = "%Y-%m-%dT%H:%M:%S"):
    """ Flags data outside of a specified time range

    Parameters
    ----------
    values : array-like
        The temperature values
    timestamps : array-like
        The timestamps corresponding to the temperature values
    start : Union[str, datetime,None], optional
        The start of the time range, by default None
    end : Union[str, datetime,None], optional
        The end of the time range, by default None
    invert : bool, optional
        Invert the filter, selecting data outside the time range by default False
    timeformat : str, optional
        The format of the timestamps, by default "%Y-%m-%dT%H:%M:%S"
        
    Returns
    -------
    boolean array
        True when the measured temperature value is outside the time range (if invert=False) or
        inside the time range (if invert=True)
    """
    if (start is None) or (start == "None"):
        start = np.min(timestamps)
    if (end is None) or (end == "None"):
        end = np.max(timestamps)

    if isinstance(start, str):
        start = datetime.strptime(start, timeformat)
    if isinstance(end, str):
        end = datetime.strptime(end, timeformat)
    
    flag = (timestamps >= start) & (timestamps <= end)

    if invert:
        flag = ~flag

    return flag


def ESJSD_filter(values, depths, n: int=7):
    """
    Flags data that deviates too far from the time series mean
    """
    result = np.zeros_like(values, dtype=bool)
    for d in depths.unique():
        i = (depths == d)
        result[i] = values[i] > (np.nanmean(values[i]) + n * np.power(np.sqrt(np.nanstd(values)), 1.3))
    
    return result

