import threading
from typing import Dict

# ------------------------------------------------------------------------------------------------ #
from src.tasks.heartbeat import heartbeat
from src.tasks.httpServer import httpServer
from src.tasks import camera
from src.tasks import aws

from src import BscbAPI

TASK_THREADS: Dict[str, threading.Thread] = {
    "heartbeat": heartbeat.create_thread(),
    "http_server": httpServer.create_thread(),
    "camera": camera.create_thread(),
    "control": BscbAPI.create_thread(),
    "aws": aws.create_thread(),
}


def start_all_threads():
    for thread in TASK_THREADS.values():
        if not thread.is_alive():
            # thread.daemon = True
            thread.start()


# __all__ = ["TASK_THREADS", "TASK_KILLER", start_all_threads()]
