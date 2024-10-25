from periphery import GPIO
import time
from functools import wraps


# !OBSOLETE
# Debounce decorator that tracks state changes during function execution
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
            # Get initial state with debouncing
            initial_state = read_sensor_with_debounce(gpio_pin, debounce_time)

            # Call the decorated function
            result = func(*args, **kwargs)

            # Check the state again after the function execution
            final_state = read_sensor_with_debounce(gpio_pin, debounce_time)

            # Determine if the state has changed
            state_changed = initial_state != final_state

            # Return the result of the function and whether the state changed
            return result, state_changed

        return wrapper

    return decorator


# Function to read the state of the sensor with debouncing
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
            # Read the current state of the sensor
            current_state = gpio.read()

            # If the state changes, reset the debounce timer
            if current_state != last_state:
                last_state = current_state
                last_stable_time = time.time()

            # If the state has been stable for the debounce time, confirm the state
            if time.time() - last_stable_time >= debounce_time:
                if stable_state != current_state:
                    stable_state = current_state
                    # Return the current stable state
                    return "high" if stable_state == 1 else "low"

            time.sleep(0.01)  # Small delay to avoid busy-waiting

    except KeyboardInterrupt:
        print("Exiting program")

    finally:
        gpio.close()
