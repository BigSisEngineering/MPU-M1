import threading
from typing import Dict

# ------------------------------------------------------------------------------------------------ #
from src.tasks import camera
from src.tasks import aws
from src.tasks import find_circle
from src.tasks import log_data

from src import BscbAPI

TASK_THREADS: Dict[str, threading.Thread] = {
    "log_data": log_data.create_thread(),
    "camera": camera.create_thread(),
    "control": BscbAPI.create_thread(),
    "aws": aws.create_thread(),
    "find_circle": find_circle.create_thread(),
}


def start_all_threads():
    for thread in TASK_THREADS.values():
        thread.start()
