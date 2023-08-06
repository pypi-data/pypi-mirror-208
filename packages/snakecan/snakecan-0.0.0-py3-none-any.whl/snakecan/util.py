from enum import Enum
from typing import Optional
import os

def chartoint(char):
    if isinstance(char, str):
        return ord(char)
    return char

def iscntrl(char):
    return chartoint(char) < 32 or chartoint(char) == 127

def isascii(char):
    return chartoint(char) <= 127

def toascii(c):
    return chr(chartoint(c) & 0x7f)


class VTColor(Enum):
    #                  FrG, BkG
    BLACK          = (  30,  40)
    RED            = (  31,  41)
    GREEN          = (  32,  42)
    YELLOW         = (  33,  43) 
    BLUE           = (  34,  44)
    MAGENTA        = (  35,  45)
    CYAN           = (  36,  46)
    WHITE          = (  37,  47)
    BRIGHT_BLACK   = (  90, 100)
    BRIGHT_RED     = (  91, 101)
    BRIGHT_GREEN   = (  92, 102)
    BRIGHT_YELLOW  = (  93, 103) 
    BRIGHT_BLUE    = (  94, 104)
    BRIGHT_MAGENTA = (  95, 105)
    BRIGHT_CYAN    = (  96, 106)
    BRIGHT_WHITE   = (  97, 107)
    

def vt_hyperlink(text, link):
    return f'\033]8;;{link}\033\\{text}\033]8;;\033\\'

def vt_color(text, foreground: Optional[VTColor] = None, background=None, bold=False):
    return f'\033[{foreground.value[0] if foreground != None else 1};1m{text}\033[0m'



def plat_is_windows():
    return os.name == 'nt'

