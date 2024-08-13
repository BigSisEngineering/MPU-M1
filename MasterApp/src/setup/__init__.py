import os
import configparser
import socket
import json

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
    """
    hostname format M1-{row}-M
    """
    id = socket.gethostname() if arg is None else arg

    if id:
        parts = id.split("-")
        if len(parts) > 1:
            number = int(parts[1])
            CLI.printline(Level.INFO, f"(setup)-Master for row: {number}")
            return number

    CLI.printline(Level.ERROR, f"(setup)-Incorrect hostname format! Please reinstall the software")
    return None


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


def get_setup_info() -> bytes:
    global ROW, SOFTWARE_VERSION

    dict = {}
    dict["module"] = 1
    dict["row"] = ROW
    dict["software_version"] = SOFTWARE_VERSION

    return json.dumps(dict).encode()
