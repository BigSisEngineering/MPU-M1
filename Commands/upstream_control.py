import requests  # pip install requests

startID = 12
endID = 13


def clear_star_wheel_error():
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/CLEAR_STAR_WHEEL_ERROR"
            # print(url)
            requests.post(url, timeout=0.4)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"{n:02} - Failed")


def clear_unloader_error():
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/CLEAR_UNLOADER_ERROR"
            # print(url)
            requests.post(url, timeout=0.4)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"{n:02} - Failed")
            print(f"{n:02} - Failed")


def star_wheel_init():
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/STAR_WHEEL_INIT"
            # print(url)
            requests.post(url, timeout=0.4)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"{n:02} - Failed")
            print(f"{n:02} - Failed")


def unloader_init():
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/UNLOADER_INIT"
            # print(url)
            requests.post(url, timeout=0.4)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"{n:02} - Failed")


def start_dummy():
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/ENABLE_DUMMY"
            # print(url)
            requests.post(url, timeout=0.4)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"(Error)-{e}")
            print(f"{n:02} - Failed")


def start_pnp():
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/ENABLE_PNP"
            # print(url)
            requests.post(url, timeout=0.4)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"(Error)-{e}")
            print(f"{n:02} - Failed")


def stop_dummy():
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/DISABLE_DUMMY"
            # print(url)
            requests.post(url, timeout=2)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"(Error)-{e}")
            print(f"{n:02} - Failed")


def stop_pnp():
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/DISABLE_PNP"
            # print(url)
            requests.post(url, timeout=2)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"(Error)-{e}")
            print(f"{n:02} - Failed")


def set_star_wheel_speed(ms=600):
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/SET_STAR_WHEEL_SPEED/{ms}"
            # print(url)
            requests.post(url, timeout=1)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"(Error)-{e}")
            print(f"{n:02} - Failed")


def set_unload_probability(prob=100):
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/SET_DUMMY_UNLOAD_PROBABILITY/{prob}"
            # print(url)
            requests.post(url, timeout=0.8)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"(Error)-{e}")
            print(f"{n:02} - Failed")


def set_pnp_confidence(prob=100):
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/SET_PNP_CONFIDENCE_LEVEL/{prob}"
            # print(url)
            requests.post(url, timeout=1)
            print(f"{n:02} - OK")
        except Exception as e:
            print(f"(Error)-{e}")
            print(f"{n:02} - Failed")


def get_unloaded_pot_number():
    for n in range(startID, endID):
        try:
            url = f"http://cage0x00{n:02}:8080/potData"
            # print(url)
            res = requests.get(url, timeout=1).json()
            print(f"{n:02} - {res}")
        except Exception as e:
            print(f"(Error)-{e}")
            print(f"{n:02} - Failed")


if __name__ == "__main__":
    import time

    # clear_star_wheel_error()
    # clear_unloader_error()

    # star_wheel_init()
    # unloader_init()
    # set_star_wheel_speed(600)
    # set_unload_probability(50)
    # set_pnp_confidence(5)
    # start_dummy()
    # start_pnp()

    # stop_dummy()
    stop_pnp()

    # get_unloaded_pot_number()

# in:10
# get:
