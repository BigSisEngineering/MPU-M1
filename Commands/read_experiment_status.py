import requests
import threading
import time

killer = threading.Event()


def get_experiment_status(hostname, result_dict, retries=2, delay=0):
    url = f"http://{hostname}.local:8080/ExperimentData"

    for attempt in range(retries):
        try:
            response = requests.get(url=url, timeout=50)
            if response.status_code == 200:
                result_dict[hostname] = f"{hostname}: {response.text.strip()}"
                return
            else:
                result_dict[hostname] = f"{hostname}: received status {response.status_code}"

        except requests.exceptions.RequestException as e:
            result_dict[hostname] = f"{hostname}: error occurred, attempt {attempt + 1}"

        time.sleep(delay)

    result_dict[hostname] = f"{hostname}: failed after {retries} attempts"


def print_data(row: int):
    global killer

    row = row - 1

    # initialize dict
    result_dict = {}
    for i in range(1, 15):
        hostname = f"cage{row}x{str(i).zfill(4)}"
        result_dict[hostname] = ""

    while not killer.is_set():
        try:
            threads = []
            for i in range(1, 15):
                hostname = f"cage{row}x{str(i).zfill(4)}"
                threads.append(
                    threading.Thread(
                        target=get_experiment_status,
                        args=(
                            hostname,
                            result_dict,
                        ),
                    )
                )

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            for i in range(1, 15):
                hostname = f"cage{row}x{str(i).zfill(4)}"
                print(result_dict[hostname])

            print("\n========================================================================\n")
            time.sleep(5)

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    # ===================================== Start row ==================================== #
    threading.Thread(target=print_data, args=(3,)).start()
    threading.Thread(target=print_data, args=(4,)).start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("event killer set")
            killer.set()
            break
