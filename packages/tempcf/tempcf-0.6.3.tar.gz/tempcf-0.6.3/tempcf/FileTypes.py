NTGS = "ntgs"
GTNP = "gtnp"
GP5W = 'gp5w'
FG2 = 'fg2'
GEOPREC = "geoprecision"
HOBO = "HOBOware"
RBR = "RBR"


def file_open_extensions(type: str) -> "list[tuple[str, str]]":
    text_files = ("text files", "*.csv *.txt")
    rbr_files = ("rbr files", "*.rsk *.hex *.dat *.xls *.xlsx")
    all_files = ("all files", "*.*")

    _file_open_extensions = {
        NTGS: [text_files, all_files],
        GTNP :[text_files, all_files],
        GEOPREC: [text_files, all_files],
        HOBO: [text_files, all_files],
        RBR: [rbr_files]
    }

    filetypes = _file_open_extensions.get(type, [all_files])

    return(filetypes)
