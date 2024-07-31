import os
import configparser
import socket
import re

# ------------------------------------------------------------------------------------------------ #
from src.CLI import Level
from src import CLI

ROW: int = None
MASTER_SERVER_PORT: str = None
SOFTWARE_VERSION: str = None

config_parser = configparser.ConfigParser()
config_parser.read(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "DEFAULT.ini",
    )
)


def get_row(arg=None):
    # Apply default if no argument given
    # id = socket.gethostname() if arg is None else arg
    # if id:
    #     match = re.search(r"x(\d+)", id)
    #     if match:
    #         number = int(match.group(1))
    #         CLI.printline(Level.INFO, f"(setup)-Master for row: {number}")
    #         return int(id[-2:])

    # CLI.printline(Level.ERROR, f"(setup)-Incorrect hostname format! Please reinstall the software")
    CLI.printline(Level.WARNING, f"(setup)-Mock row set to 7")
    return 7


def get_master_server_port(arg=None):
    port = config_parser.get("ROW_MASTER", "HTTP_SERVER_PORT") if arg is None else arg
    CLI.printline(Level.INFO, f"(setup)-Master HTTP server port set: {port}")
    return port


def get_software_version(arg=None):
    version = config_parser.get("VERSION", "SOFTWARE") if arg is None else arg
    CLI.printline(Level.INFO, f"(setup)-Software version: {version}")
    return version


ROW = get_row()
MASTER_SERVER_PORT = get_master_server_port()
SOFTWARE_VERSION = get_software_version()


# ------------------------------------------------------------------------------------ #
def debug():
    print(ROW)

    print(type(ROW))
