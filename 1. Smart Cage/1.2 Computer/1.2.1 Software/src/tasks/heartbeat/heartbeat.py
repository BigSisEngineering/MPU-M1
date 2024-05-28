import threading
import requests  # pip install requests
import time

# ------------------------------------------------------------------------------------------------ #
from src import CLI, setup
from src.CLI import Level
from src import comm

KILLER = threading.Event()


def is_host_server_exist(ip_port=None):
    ip_port = f"{setup.MASTER_IP}:{setup.MASTER_SERVER_PORT}" if ip_port is None else ip_port
    try:
        requests.get(f"http://{ip_port}/ACK")
        return True
    except requests.exceptions.ConnectionError:
        return False


def loop(stop_event: threading.Event, ip_port: str = None):
    ip_port = f"{setup.MASTER_IP}:{setup.MASTER_SERVER_PORT}" if ip_port is None else ip_port
    while not stop_event.is_set():
        ping_master(ip_port)
    CLI.printline(Level.ERROR, "(Heartbeat)-thread terminated.")


@comm.timing_decorator(interval_s=5)
def ping_master(ip_port):
    try:
        requests.get(f"http://{ip_port}/ACK")
        CLI.printline(Level.DEBUG, f"(Heartbeat)-PINGED")

    except Exception:
        CLI.printline(Level.WARNING, f"Host({ip_port}) server is down")


def create_thread():
    global KILLER
    return threading.Thread(target=loop, args=(KILLER,))


if __name__ == "__main__":
    DESTINATION = "192.168.73.212:8080"
    # thread_heart_beat_to_rowmaster(DESTINATION)  # Start the initial heartbeat

    # Keep the main thread alive, can be ignored
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Heartbeat stopped.")
