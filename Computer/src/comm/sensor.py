from periphery import GPIO
import time
from functools import wraps


# !OBSOLETE
def debounce_sensor(gpio_pin, debounce_time=0.05):
    """
    Decorator that adds sensor debouncing and checks if the sensor state changes during function execution.

    Args:
    gpio_pin (int): The GPIO pin number to monitor.
    debounce_time (float): The debounce time in seconds.

    Returns:
    (function result, bool): The result of the decorated function and True if the sensor state changed, False otherwise.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            initial_state = read_sensor_with_debounce(gpio_pin, debounce_time)
            result = func(*args, **kwargs)
            final_state = read_sensor_with_debounce(gpio_pin, debounce_time)
            state_changed = initial_state != final_state
            return result, state_changed

        return wrapper

    return decorator

def read_sensor_with_debounce(gpio_pin, debounce_time=0.05):
    """
    Reads a GPIO pin with debouncing to avoid false triggers.

    Args:
    gpio_pin (int): The GPIO pin number to read from.
    debounce_time (float): The time in seconds to wait for debounce filtering. Default is 50ms.

    Returns:
    str: "high" if the sensor is triggered, "low" otherwise.
    """
    gpio = GPIO(gpio_pin, "in")

    last_state = gpio.read()
    stable_state = last_state
    last_stable_time = time.time()

    try:
        while True:
            current_state = gpio.read()
            if current_state != last_state:
                last_state = current_state
                last_stable_time = time.time()
            if time.time() - last_stable_time >= debounce_time:
                if stable_state != current_state:
                    stable_state = current_state
                    return "high" if stable_state == 1 else "low"
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Exiting program")

    finally:
        gpio.close()
