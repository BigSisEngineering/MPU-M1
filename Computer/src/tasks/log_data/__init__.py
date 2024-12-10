import re
from datetime import datetime, timedelta
import time
import threading
import socket
import logging
import os

from src import CLI
from src.CLI import Level
from src import data


# Ensure the log file is created if it doesn't exist
log_file = f"{socket.gethostname()}.log"
if not os.path.exists(log_file):
    open(log_file, "a").close()

# Set up the logger
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")

def delete_old_files_from_log(log_file, days_old=3):
    # Read the log file
    def read_log_file(file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                lines = file.readlines()
                return [line.strip() for line in lines]
        else:
            logging.error(f"Log file {file_path} does not exist.")
            return []

    # Parse the timestamp from the filename
    def parse_timestamp_from_filename(filename):
        parts = filename.split("_")
        if len(parts) == 10:
            timestamp_str = f"{parts[1]}-{parts[2]}-{parts[3]} {parts[4]}:{parts[5]}:{parts[6]}"
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return None

    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=days_old)
    remaining_files = []

    # Process the log file
    file_paths = read_log_file(log_file)
    for path in file_paths:
        filename = os.path.basename(path)
        timestamp = parse_timestamp_from_filename(filename)

        if timestamp and timestamp < cutoff_date:
            try:
                os.remove(path)
                logging.info(f"Deleted file: {path}")
            except Exception as e:
                logging.error(f"Error deleting file {path}: {e}")
        else:
            remaining_files.append(path)

    # Update the log file
    with open(log_file, "w") as file:
        for line in remaining_files:
            file.write(f"{line}\n")

    CLI.printline(Level.INFO, f"(log) Old files deleted and log file updated.")


def delete_old_log_entries(log_file, days_old=3):
    cutoff_date = datetime.now() - timedelta(days=days_old)
    remaining_entries = []

    # Keywords to identify error messages
    error_keywords = [
        "Traceback",
        "Error",
        "Exception",
        "File",
        "TimeoutError",
        "OSError",
        "execute(self.server.app)",
        "write(data)",
        "self.wfile.write(data)",
        "self._sock.sendall(b)",
        "for data in application_iter:",
        "return self._next()",
        "print",
        "frame = bbox.draw(",
        "for item in iterable:",
    ]

    # Read and filter log entries
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            for line in file:
                # Skip lines containing error keywords
                if any(keyword in line for keyword in error_keywords):
                    continue

                if "at" in line:
                    timestamp_str = line.split("at")[-1].strip()
                    try:
                        log_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        if log_timestamp >= cutoff_date:
                            remaining_entries.append(line)
                    except ValueError as e:
                        logging.error(f"Error parsing timestamp from log entry: {line}. Error: {e}")
                        remaining_entries.append(line)
                else:
                    remaining_entries.append(line)

        # Write the remaining entries back to the log file
        with open(log_file, "w") as file:
            file.writelines(remaining_entries)

    else:
        logging.error(f"Log file {log_file} does not exist.")

    CLI.printline(Level.INFO, f"(log) Old log entries and errors deleted, log file updated.")

def count_eggs_last_hour(log_file_path):
    current_time = datetime.now()
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
# Call the function to delete old log entries
delete_old_log_entries(log_file, days_old=4)

# Call the function to delete old files and update the log file
delete_old_files_from_log(log_file, days_old=4)

def get_log_data_thread(stop_event: threading.Event):
    time_stamp = time.time()
    watchdog = 60

    while not stop_event.is_set():
        try:
            if (time.time() - time_stamp) > watchdog:
                time_stamp = time.time()
                count_score_positive, count_total = count_eggs_last_hour(log_file)

                with data.lock:
                    data.eggs_last_hour = count_score_positive
                    data.steps_last_hour = count_total

        except Exception as e:
            CLI.printline(Level.ERROR, f"(get_log_data_thread)-{e}")
            continue


def create_thread():
    global KILLER
    return threading.Thread(target=get_log_data_thread, args=(KILLER,))
