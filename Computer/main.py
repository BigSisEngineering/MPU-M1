from src import CLI
from src.CLI import Level
import threading

from src import tasks
from src.tasks import httpServer


def main():
    CLI.printline(Level.INFO, "Start")
    # tasks.start_all_threads()
    # httpServer.start_server()
    server_thread = threading.Thread(target=httpServer.start_server)
    server_thread.start()
    tasks.start_all_threads()
    server_thread.join()


# ------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    main()
