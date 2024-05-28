from src import CLI
from src.CLI import Level

from src import tasks


def main():

    CLI.printline(Level.INFO, f"Start")

    tasks.start_all_threads()


# ------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    main()
