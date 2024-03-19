import time

# ------------------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

from src import tasks
from src import BscbAPI

from src import app
from src.app import utils, session


@utils.main_display
def main():
    app.write()
    key = session.generate_random_string()

    CLI.printline(Level.INFO, f"Key generated: {key}")

    tasks.start_all_threads()
    with session.lock:
        session.KEY = key

    is_new_run = True
    while True:
        with session.lock:
            global_key = session.KEY

        if global_key == key:
            # DO THE UI UPDATE HERE
            app.update(is_new_run)
            app.play_frame()
            # BscbAPI.execute()
            is_new_run = False

        else:
            app.logout()
            break

        # time.sleep(1 / 24)


# @comm.timing_decorator(interval_s=2)
# def ui_loop():
#     print("hello")


if __name__ == "__main__":
    main()
