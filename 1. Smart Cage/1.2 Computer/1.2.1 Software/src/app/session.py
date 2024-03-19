import random
import string
import threading

lock = threading.Lock()
KEY: str = ""


def generate_random_string(length=5):
    """
    Generate a random string of the specified length.
    """
    characters = string.ascii_letters + string.digits  # Use letters and digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string
