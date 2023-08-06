# tempcf Log Parser

import argparse
import pandas as pd
import pathlib

def pathExists(path):
    if pathlib.Path(path).exists():
        return path
    else:
        raise argparse.ArgumentTypeError(f"The path specified does not exist: {path}")

def getMetadata(log):
    # Metadata are expected to be in a particular order
    metadata_tags = ["created", "tempcf_version", "original_file", "unique_times", "unique_depths"]
    metadata = {}
    for tag in metadata_tags:
        metadata[tag] = log.readline().rstrip("\n")
    try:
        for key, value in metadata.items():
            metadata[key] = metadata[key].split(": ", 1)[1]
    except IndexError:
        raise ValueError("Metadata values were unable to be parsed correctly.\nLog metadata should be left unchanged after creation.")
    return metadata    

def parseLog(logPath):
    with open(logPath) as fp:
        try:
            metadata = getMetadata(fp)
        except ValueError as err:
            raise RuntimeError(f"Failed metadata parsing: \n{err}")
        changes = pd.read_csv(logPath, keep_default_na=True, float_precision="round_trip", skiprows=len(metadata))
        if len(changes) == 0:
            raise ValueError("The log file did not have any changes to read in!")
    return metadata, changes

def applyLogChanges(log, df):
    """Merges a dataframe of changes from a log file with another dataframe.
    
    Interprets time column as pandas datetime in order to properly merge.
    Finds matching values from the original values recorded in the log and existing temperature values in the merged dataframe (based on time and depth) to crate a boolean mask.
    Changes matching values to the new values from the log dataframe.
    log --- a dataframe from a log file, see return value 'changes' from parseLog
    df --- a dataframe to merge with the log file changes dataframe
    """
    log["original_date"] = pd.to_datetime(log["original_date"])
    df = pd.merge(df, log, how="left", left_on=["time", "depth", "temperature"], right_on=["original_date", "original_depth", "original_value"])
    mask = (df["temperature"] == df["original_value"])
    df.loc[mask, "temperature"] = df.loc[mask, "new_value"]
    df.drop(columns=["original_date", "original_depth", "original_value", "new_value"], inplace=True)
    return df

if __name__ == '__main__':
    # import pprint
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="description")
    parser.add_argument('logfile', metavar='filepath', type=pathExists, help='Path to file')
    arguments = vars(parser.parse_args())
    # logContents = arguments['logfile'].read()
    # arguments['logfile'].close()
    # meta, rows = parseLog(arguments['logfile'])
    # pprinter = pprint.PrettyPrinter(indent=4, sort_dicts=False)
    # pprinter.pprint(meta)
