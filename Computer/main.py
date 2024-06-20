import time
from src import CLI
from src.CLI import Level

from src import tasks
from src.tasks import httpServer
from src.BscbAPI.BscbAPI import BScbAPI

# print('start unloader init')
# BScbAPI(baud_rate=115200).unloader_init()

# time.sleep(2)
# print('start SW init')
# BScbAPI(baud_rate=115200).starWheel_init()

def main():

    CLI.printline(Level.INFO, f"Start")

    tasks.start_all_threads()
    httpServer.start_server()


# ------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    main()
