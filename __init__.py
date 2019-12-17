import inspect
import os
import re

SCREEN_CODES = {
    "black": "30",
    "lblack": "90",
    "xblack": "40",
    "xbblack": "100",
    "red": "31",
    "lred": "91",
    "xred": "41",
    "xbred": "101",
    "green": "32",
    "lgreen": "92",
    "xgreen": "42",
    "xbgreen": "102",
    "yellow": "33",
    "lyellow": "93",
    "xyellow": "43",
    "xbyellow": "103",
    "blue": "34",
    "lblue": "94",
    "xblue": "44",
    "xbblue": "104",
    "magenta": "35",
    "lmagenta": "95",
    "xmagenta": "45",
    "xbmagenta": "105",
    "cyan": "36",
    "lcyan": "96",
    "xcyan": "46",
    "xbcyan": "106",
    "white": "37",
    "lwhite": "97",
    "xwhite": "47",
    "xbwhite": "107",
    "z": "0",
    "b": "1",
    "xb": "2",
    "i": "3",
    "u": "4",
    "blink": "5",
    "xblink": "6",
    "x": "7",
    "c": "8",
    "s": "9",

}

SHORT_CODES = {}
MACROS = {}

def enableShortCode(short, expand):
    if not short in SHORT_CODES:
        SHORT_CODES[short] = expand
    else:
        return

def enableMacro(short, function):
    if not short in MACROS:
        MACROS[short] = function
    else:
        return

def printx(*args, **kwargs):
    tToPrint = ""
    regex = re.compile(r"<((?:\:[A-Za-z0-9_]+)+)[ \t]+'([^>]*)'>")
    regex2 = re.compile(r"<((?:\:[A-Za-z0-9_]+)+)>")

    def replacer(match):
        groups = match.groups()
        string = ""
        if len(groups) > 1:
            string = groups[1]
        groups = filter(lambda x: len(x) > 0, groups[0].split(":"))
        groups = [x for x in groups]
        colors = []
        padding = 0
        length = None
        tabs = 0
        center = False
        lf = False
        for i in range(0, len(groups)):
            if groups[i].startswith("bg"):
                color = groups[i].replace("bg","")
                colors.append("38;5;" + color)
            elif groups[i].startswith("fg"):
                color = groups[i].replace("fg","")
                colors.append("48;5;" + color)
            elif groups[i].startswith("pad"):
                padding = int(groups[i].replace("pad",""))
            elif groups[i].startswith("len"):
                length = int(groups[i].replace("len",""))
            elif groups[i].startswith("tab"):
                tabs = int(groups[i].replace("tab",""))
            elif groups[i] == "center":
                center = True
            elif groups[i] == "right":
                center = 1
            elif groups[i] == "left":
                center = -1
            elif groups[i] == "plf":
                string = "\n" + string
            elif groups[i] == "lf":
                lf = True
            elif groups[i] in SHORT_CODES:
                string = SHORT_CODES[groups[i]]
            elif groups[i] in MACROS:
                string = MACROS[groups[i]](string)
            else:
                colors.append(SCREEN_CODES[groups[i]])
        if length != None and len(string) < length:
            if isinstance(center, bool) and center:
                diff = length - len(string)
                if diff % 2 == 0:
                    string = " " * round(diff / 2) + string + " " * round(diff / 2)
                else:
                    string = " " * round(diff / 2) + string + " " * round((diff + 1) / 2)
            elif center == 1:
                diff = length - len(string)
                string = " "*diff + string
            else:
                string = string + " " * (length - len(string))
        string = " " * padding + string + " " * padding
        return ("\n" if lf else "") + "\033[" + ";".join(colors) + "m" + "\t"*tabs + string + "\033[0m\033[22;0m"

    for i in range(0, len(args)):
        arg = args[i]
        if arg and isinstance(arg, str):
            if regex2.search(arg):
                arg = regex2.sub(replacer, arg)
            arg = regex.sub(replacer, arg)
            tToPrint += arg + " "
        else:
            tToPrint += str(arg) + " "
    if len(regex.findall(tToPrint)) or len(regex2.findall(tToPrint)):
        tToPrint = printx(tToPrint, ret=True)
    print_args = {}
    tTemp = re.compile(r"\033\[([0-9]+;?)*m").sub(lambda x: "", tToPrint).strip(" \t\n\r")
    if "force_empty" in kwargs:
        if not kwargs["force_empty"] and len(tTemp) == 0:
            return
    if "lf" in kwargs:
        if kwargs["lf"]:
            print_args["end"] = ""
            print_args["flush"] = True
    if "print" in kwargs:
        if not kwargs["print"]:
            return
    if "ret" in kwargs:
        if kwargs["ret"]:
            return tToPrint
    print(tToPrint, **print_args)