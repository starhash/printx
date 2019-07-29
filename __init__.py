import re

SCREEN_CODES = {
    "black": "30",
    "xblack": "40",
    "red": "31",
    "xred": "41",
    "green": "32",
    "xgreen": "42",
    "yellow": "33",
    "xyellow": "43",
    "blue": "34",
    "xblue": "44",
    "magenta": "35",
    "xmagenta": "45",
    "cyan": "36",
    "xcyan": "46",
    "white": "37",
    "xwhite": "47",
    "z": "0",
    "b": "1",
    "xb": "2",
    "i": "3",
    "u": "4",
    "blink": "5",
    "xblink": "6",
    "x": "7",
    "c": "8",
    "s": "9"
}

SHORT_CODES = {}

def enableShortCode(short, expand):
    if not short in SHORT_CODES:
        SHORT_CODES[short] = expand
    else:
        return
        

def printx(*args):
    tToPrint = ""
    regex = re.compile(r"<((?:\:[a-z0-9]+)+)[ \t]+'([^\:]+)'>")

    def replacer(match):
        groups = match.groups()
        string = groups[1]
        groups = filter(lambda x: len(x) > 0, groups[0].split(":"))
        groups = [x for x in groups]
        print(groups)
        colors = []
        padding = 0
        length = None
        center = False
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
            elif groups[i] == "center":
                center = True
            else:
                colors.append(SCREEN_CODES[groups[i]])
        if length != None and len(string) < length:
            if center:
                diff = length - len(string)
                if diff % 2 == 0:
                    string = " " * round(diff / 2) + string + " " * round((diff + 1) / 2)
                else:
                    string = " " * round(diff / 2) + string + " " * round(diff / 2)
            else:
                string = string + " " * (length - len(string))
        string = " " * padding + string + " " * padding
        return "\033[" + ";".join(colors) + "m" + string + "\033[0m"

    for i in range(0, len(args)):
        arg = args[i]
        arg = regex.sub(replacer, arg)
        tToPrint += arg + " "
    print(tToPrint)