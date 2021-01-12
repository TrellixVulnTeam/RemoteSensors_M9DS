"""
Misc utilities and global variables
"""
from datetime import datetime


CODECS = ["AGIF", "FLAC", "H263", "H264", "H265", "MJPA", "MJPB", "MJPG", "MPG2",
          "MPG4", "MVC0", "PCM", "THRA", "VORB", "VP6", "VP8", "WMV9", "WVC1"]


#
REFRESH = 0.5
MAX_BAR_COLS = 50
MAX_TEMP = 70
FINALIZE = False
UPDATE_DISK_INFO = False
HUMAN_DISK_INFO = True


def get_time():
    """
    Returns the curent time in HH:MM:SS format
    """
    return str(datetime.now().time().replace(microsecond=0))


def prepare_codecs(raw_codecs):
    """
    Parses the codecs info and created a list with enabled ones only
    :param raw_codecs: List of codecs provided by vcgencmd
    :return: Enabled codecs
    """
    out = []

    for item in raw_codecs:
        aux = item.split("=")
        if str(aux[1]).startswith("e"):
            out.append(aux[0])

    return out
