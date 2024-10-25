import requests
import threading
import time
import datetime

# set row
row = 1

# initialize dict
result_dict = {}
for i in range(1, 15):
    hostname = f"cage{row}x{str(i).zfill(4)}"
    result_dict[hostname] = ""


def get_experiment_status(hostname, retries=2, delay=0):
    url = f"http://{hostname}.local:8080/ExperimentData"

    for attempt in range(retries):
        try:
            response = requests.get(url=url, timeout=50)
            if response.status_code == 200:
                result_dict[hostname] = f"{hostname}: {response.text.strip()}"
                return  # Exit function if successful
            else:
                result_dict[hostname] = f"{hostname}: received status {response.status_code}"

        except requests.exceptions.RequestException as e:
            # Log the exception or response failure
            result_dict[hostname] = f"{hostname}: error occurred, attempt {attempt + 1}"

        # Delay before retrying
        time.sleep(delay)

    # If all retries fail, set a final error message
    result_dict[hostname] = f"{hostname}: failed after {retries} attempts"


if __name__ == "__main__":
    now = datetime.datetime.now()
    total_seconds = now.hour * 3600 + now.minute * 60 + now.second

    # 14 minutes in seconds
    interval_seconds = 14 * 60

    # Get the interval index, cycling through 0, 1, 2, 3, 4
    interval_index = (total_seconds // interval_seconds) % 5

    print(interval_index)
    # row = row - 1
    # while True:
    #     try:
    #         threads = []
    #         for i in range(1, 15):
    #             hostname = f"cage{row}x{str(i).zfill(4)}"
    #             threads.append(threading.Thread(target=get_experiment_status, args=(hostname,)))

    #         for thread in threads:
    #             thread.start()

    #         for thread in threads:
    #             thread.join()

    #         for i in range(1, 15):
    #             hostname = f"cage{row}x{str(i).zfill(4)}"
    #             print(result_dict[hostname])

    #         print("\n========================================================================\n")
    #         time.sleep(5)

    #     except KeyboardInterrupt:
    #         break
