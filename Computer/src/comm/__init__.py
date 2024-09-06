import time

# ------------------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level


def timing_decorator(interval_s):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_timestamp = getattr(wrapper, "last_timestamp", 0)
            if (time.time() - last_timestamp) >= interval_s:
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    result = None  # Handle exceptions as needed
                wrapper.last_timestamp = time.time()
                return result
            else:
                return None  # Function not executed within the specified interval

        return wrapper

    return decorator


def timer():
    def decorator(func):
        def wrapper(*args, **kwargs):
            timestamp = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                result = None  # Handle exceptions as needed
            time_diff = time.time() - timestamp
            CLI.printline(Level.SPECIFIC, f"[{func.__name__}] - took: {time_diff}")
            return result

        return wrapper

    return decorator
