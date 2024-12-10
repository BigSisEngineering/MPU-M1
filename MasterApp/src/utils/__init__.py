import time


class WarningTimer:
    def __init__(self, time_until_warning: float):
        self.time_stamp = time.time()
        self.time_until_warning = time_until_warning

    def reset_timer(self):
        self.time_stamp = time.time()

    @property
    def is_overtime(self) -> bool:
        return time.time() - self.time_stamp > self.time_until_warning
