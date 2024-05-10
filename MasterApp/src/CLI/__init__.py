import queue
from datetime import datetime
from enum import Enum

# ------------------------------------------------------------------------------------------------ #

# ANSI escape codes for text color
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class Level(Enum):
    DEBUG = " DEBUG "
    INFO = " INFO  "
    WARNING = "WARNING"
    ERROR = " ERROR "


# ======================================== Messages Queue ======================================== #
display = {
    Level.DEBUG: True,
    Level.INFO: True,
    Level.WARNING: True,
    Level.ERROR: True,
}

info_msgs_queue = queue.Queue()
debug_msgs_queue = queue.Queue()
warn_msgs_queue = queue.Queue()
error_msgs_queue = queue.Queue()


def printline(level: Level, msg: str):
    now = datetime.now().time().strftime("%H:%M:%S")  # time object
    date = datetime.now().strftime("%m-%d")  # date object
    msg = f"[{level.value}]-({date}/{now})-{msg}"
    if display[level]:
        if level == Level.DEBUG:
            print(BLUE + msg + RESET)
        elif level == Level.INFO:
            print(GREEN + msg + RESET)
        elif level == Level.WARNING:
            print(YELLOW + msg + RESET)
        elif level == Level.ERROR:
            print(RED + msg + RESET)
        else:
            print(msg)
    debug_msgs_queue.put(msg) if level == Level.DEBUG else None
    info_msgs_queue.put(msg) if level == Level.INFO else None
    warn_msgs_queue.put(msg) if level == Level.WARNING else None
    error_msgs_queue.put(msg) if level == Level.ERROR else None


if __name__ == "__main__":
    display[Level.DEBUG] = True
    display[Level.INFO] = True
    display[Level.WARNING] = True
    display[Level.ERROR] = True
    printline(Level.DEBUG, "testing debug")
    printline(Level.INFO, "testing INFO")
    printline(Level.WARNING, "testing WARNING")
    printline(Level.ERROR, "testing ERROR")
