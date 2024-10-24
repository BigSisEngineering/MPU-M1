import requests
import threading
import time

# set row
row = 1

# initialize dict
result_dict = {}
for i in range(1, 15):
    hostname = f"cage{row}x{str(i).zfill(4)}"
    result_dict[hostname] = ""


def get_experiment_status(hostname):
    try:
        url = f"http://{hostname}.local:8080/ExperimentData"
        response = requests.get(url=url, timeout=10)
        result_dict[hostname] = f"{hostname}: {response.text.strip()}"

    except Exception as e:
        result_dict[hostname] = f"{hostname}: error occured/n"
        pass


if __name__ == "__main__":
    row = row - 1
    while True:
        try:
            threads = []
            for i in range(1, 15):
                hostname = f"cage{row}x{str(i).zfill(4)}"
                threads.append(threading.Thread(target=get_experiment_status, args=(hostname,)))

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
