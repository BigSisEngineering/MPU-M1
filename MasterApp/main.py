import threading
# ------------------------------------------------------------------------------------------------ #
from src import http_server, tasks
from src.http_server import post_handler

def main():


    tasks.start()
    http_server.start()

if __name__ == "__main__":
    main()
