import requests
import time
import threading

# ====================================== Set row ===================================== #
row = 1

# ------------------------------------------------------------------------------------ #


def get_experiment_status(hostname):
    try:
        url = f"http://{hostname}.local:8080/ExperimentData"
        response = requests.get(url=url, timeout=10)
        print(f"{hostname}: {response.text}")

    except Exception as e:
        print(f"{hostname}: error occured\n")
        pass


if __name__ == "__main__":
    row = row - 1
    while True:
        threads = []
        for i in range(1, 15):
            hostname = f"cage{row}x{str(i).zfill(4)}"
            threads.append(threading.Thread(target=get_experiment_status, args=(hostname,)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print("\n========================================================================\n")
