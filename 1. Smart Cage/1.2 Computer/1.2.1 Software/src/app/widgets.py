from enum import Enum
import threading
import queue

# ------------------------------------------------------------------------------------------------ #


class Colour(Enum):
    black = 0
    red = 1
    yellow = 2
    green = 3
    blue = 4


class ColourStatusLight:
    def __init__(self, title: str) -> None:
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.title = title
        self.state = 0
        self.pre_state = None
        self.display_state = None
        self.apply_default()

    def apply_default(self):
        with self.lock:
            self.states = 4
        self.icons = [
            "⚫",
            "🔴",
            "🟡",
            "🟢",
            "🔵",
        ]

    def get_state(self):
        with self.lock:
            return self.state

    def toggle(self):
        state = Colour.green.value if self.state is not Colour.green.value else Colour.black.value
        with self.lock:
            self.state = state

    def set_state(self, state: int):
        def constrain(n, min_n, max_n):
            return max(min(max_n, n), min_n)

        constrain(state, 0, self.states)
        with self.lock:
            self.state = state

    def set_state_with_sensor_status(self, status: int):
        if status == 1:
            self.set_green()
        elif status == 0:
            self.set_black()
        else:
            self.set_red()

    def set_yellow(self, using_queue=False):
        if not using_queue:
            with self.lock:
                self.state = Colour.yellow.value
        else:
            self.queue.put(Colour.yellow.value)

    def set_blue(self, using_queue=False):
        if not using_queue:
            with self.lock:
                self.state = Colour.blue.value
        else:
            self.queue.put(Colour.blue.value)

    def set_green(self, using_queue=False):
        if not using_queue:
            with self.lock:
                self.state = Colour.green.value
        else:
            self.queue.put(Colour.green.value)

    def set_black(self, using_queue=False):
        if not using_queue:
            with self.lock:
                self.state = Colour.black.value
        else:
            self.queue.put(Colour.black.value)

    def set_red(self, using_queue=False):
        if not using_queue:
            with self.lock:
                self.state = Colour.red.value
        else:
            self.queue.put(Colour.red.value)

    def is_changed(self):
        self.update(using_queue=True)
        if self.pre_state != self.state:
            self.pre_state = self.state
            return True
        return False

    def update(self, using_queue=False):
        if not using_queue:
            with self.lock:
                self.display_state = self.state
        else:
            if not self.queue.empty():
                self.state = self.queue.get()
            self.display_state = self.state

    def display(self):
        self.update()
        content = f"[ {self.title} {self.icons[self.display_state]}]"
        return f"<h5 style='text-align: center; color: black;'>{content}</h5>"
