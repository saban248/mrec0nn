import os
import subprocess as sub
MAX_FD_FUZZ_SIZE = 100000000
MAX_LBL_PER_LINE = 30


def OpenBruteFile(path: str) -> tuple[...,str]:
    if not path:
        return 0, "choose_file"
    if not os.path.exists(path):
        return 0, "file_not_found"
    if os.path.getsize(path) > MAX_FD_FUZZ_SIZE:
        return 0, "max_size_file"

    file = open(path, "r", errors="ignore")
    data = file.read().split("\n")
    file.close()
    if 6 < (os.path.getsize(path) / data.__len__()) < MAX_LBL_PER_LINE:
        return data, "OK"
    else:
        return 0, "file_unsupported"


def fixWidthPath(path):

    lgn = path.__len__()
    if lgn > 20:
        return path[0:5] + ".." + path[-15:]

    return path


def OpenUrl(address):
    """
    **-> your system select the specific explorer >**
    :param address: url
    :return: None
    """
    sub.Popen(f"cmd.exe /c start {address}", shell=False)


def SaveFileFuzz(path, data:list[dict], code):
    fuzz = open(path, "w")
    for page in data:
        if page['stat'] == code:
            fuzz.write(page["ind"]+"\n")

    fuzz.close()
    return 1
