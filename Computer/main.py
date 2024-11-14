import logging
import datetime
from src import CLI
from src.CLI import Level

from src import tasks
from src.tasks import httpServer

logging.info(f"Cage restarted at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
def main():
    CLI.printline(Level.INFO, "Start")
    tasks.start_all_threads()
    httpServer.start_server()


# ------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    main()
