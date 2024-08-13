from src import http_server, tasks

# ------------------------------------------------------------------------------------ #
from src._shared_variables import SV

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "MAIN"


def terminate_program():
    SV.KILLER_EVENT.set()
    CLI.printline(Level.ERROR, "({:^15}) Program Terminated.".format(print_name))


def main():
    try:
        tasks.start()
        http_server.start()
        terminate_program()

    except KeyboardInterrupt:
        terminate_program()


if __name__ == "__main__":
    main()
