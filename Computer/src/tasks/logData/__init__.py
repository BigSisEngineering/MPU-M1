import re
from datetime import datetime, timedelta
import time
import threading
import socket

from src import CLI
from src.CLI import Level
from src import data


def count_eggs_last_hour(log_file_path):
    # Get the current time
    current_time = datetime.now()

    # Calculate the start of the last hour
    start_last_hour = current_time.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

    # Initialize the counter
    count_score_positive = 0
    count_total = 0

    # Regex pattern to extract details from the filename
    pattern = re.compile(
        r".*/(?P<cage_name>[^_]+)_(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})_(?P<hour>\d{2})_(?P<min>\d{2})_(?P<sec>\d{2})_(?P<ms>\d{2})_(?P<threshold>\d+)_(?P<score>\d+)\.jpg"
    )

    with open(log_file_path, "r") as file:
        for line in file:
            match = pattern.match(line.strip())
            if match:
                file_time = datetime(
                    year=int(match.group("year")),
                    month=int(match.group("month")),
                    day=int(match.group("day")),
                    hour=int(match.group("hour")),
                    minute=int(match.group("min")),
                    second=int(match.group("sec")),
                    microsecond=int(match.group("ms")) * 10000,
                )
                score = int(match.group("score"))

                # # Check if the file is within the last hour and has a score > 0
                # if start_last_hour <= file_time < current_time and score > 0:
                #     count += 1
                # Check if the file time is within the last hour
                if start_last_hour <= file_time < current_time:
                    count_total += 1
                    # Additionally check if the score is greater than 0
                    if score > 0:
                        count_score_positive += 1

    return count_score_positive, count_total


KILLER = threading.Event()
log_file = f"{socket.gethostname()}.log"


def get_log_data_thread(stop_event: threading.Event):
    time_stamp = time.time()
    watchdog = 60  # seconds

    while not stop_event.is_set():
        try:
            if (time.time() - time_stamp) > watchdog:
                time_stamp = time.time()
                count_score_positive, count_total = count_eggs_last_hour(log_file)
                data.eggs_last_hour = count_score_positive
                data.steps_last_hour = count_total

        except Exception as e:
            CLI.printline(Level.ERROR, f"(get_log_data_thread)-{e}")
            continue


def create_thread():
    global KILLER
    return threading.Thread(target=get_log_data_thread, args=(KILLER,))
