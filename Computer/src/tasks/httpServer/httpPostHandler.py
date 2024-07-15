import time
# ------------------------------------------------------------------------------------------------ #
from src import BscbAPI
from src import data
from src.BscbAPI.BscbAPI import BScbAPI
from src.app import handler


POST_LIST = [
    "STAR_WHEEL",
    "STAR_WHEEL_INIT",
    "ALL_SERVOS_INIT",
    "UNLOADER_INIT",
    "ENABLE_DUMMY",
    "ENABLE_PNP",
    "ENABLE_PURGE",
    "DISABLE_DUMMY",
    "DISABLE_PNP",
    "SET_STAR_WHEEL_SPEED",
    "SET_DUMMY_UNLOAD_PROBABILITY",
    "SET_PNP_CONFIDENCE_LEVEL",
    "CLEAR_STAR_WHEEL_ERROR",
    "CLEAR_UNLOADER_ERROR",
    "MOVE_CW",
    "MOVE_CCW",
    "UNLOAD",
    "SET_CYCLE_TIME",
    "SAVE_STAR_WHEEL_ZERO",
    "SAVE_STAR_WHEEL_OFFSET",
    "SET_POS",
    "MOVE_STAR_WHEEL"
]


def generateFuncName(arg):
    return f"post_{arg}"


def send_200_response(server):
    server.send_response(200)
    server.send_header("Cache-Control", "no-cache, private")
    server.send_header("Pragma", "no-cache")
    server.end_headers()


def post_STAR_WHEEL(server):
    with BScbAPI("/dev/ttyACM0", 115200) as board:
        board.starWheelInit()
        for _ in range(3):
            board.starWheelMoveTime(server.parsed_url[2])
    send_200_response(server)


def post_STAR_WHEEL_INIT(server):
    send_200_response(server)
    if not data.dummy_enabled or not data.pnp_enabled:
        server.wfile.write("star wheel init will be proceed".encode())
        handler.init_star_wheel()
    else:
        server.wfile.write("Error, disable dummy/pnp".encode())


def post_UNLOADER_INIT(server):
    send_200_response(server)
    if not data.dummy_enabled or not data.pnp_enabled:
        server.wfile.write("unloader init will be proceed".encode())
        handler.init_unloader()
    else:
        server.wfile.write("Error, disable dummy/pnp".encode())


def post_ALL_SERVOS_INIT(server):
    send_200_response(server)
    if not data.dummy_enabled or data.pnp_enabled:
        server.wfile.write("all init will be proceed".encode())
        handler.init_unloader()
        handler.clear_star_wheel_error()
        handler.init_star_wheel()
    else:
        server.wfile.write("Error, disable dummy/pnp".encode())

def post_ENABLE_PNP(server):
    send_200_response(server)
    with data.lock:
        if data.servos_ready:
            data.pnp_enabled = True
            server.wfile.write("pnp Enabled".encode())
        else:
            server.wfile.write("Initialize servos first".encode())



def post_ENABLE_DUMMY(server):
    send_200_response(server)
    with data.lock:
        if data.servos_ready:
            data.dummy_enabled = True
            server.wfile.write("Dummy Enabled".encode())
        else:
            server.wfile.write("Initialize servos first".encode())

def post_ENABLE_PURGE(server):
    send_200_response(server)
    with data.lock:
        if data.servos_ready:
            data.purge_enabled = True
            server.wfile.write("Purge Started".encode())
        else:
            server.wfile.write("Initialize servos first".encode())

def post_DISABLE_DUMMY(server):
    send_200_response(server)
    server.wfile.write("Dummy Disabled".encode())
    with data.lock:
        data.dummy_enabled = False


def post_DISABLE_PNP(server):
    send_200_response(server)
    server.wfile.write("pnp Disabled".encode())
    with data.lock:
        data.pnp_enabled = False


def post_SET_STAR_WHEEL_SPEED(server):
    send_200_response(server)

    given_speed = int(server.parsed_url[2])
    if given_speed >= 600 and given_speed <= 5000:
        server.wfile.write(f"Speed set to {given_speed}".encode())
    else:
        server.wfile.write(f"speed should be 600-5000ms".encode())

    with data.lock:
        data.star_wheel_duration_ms = given_speed


def post_SET_DUMMY_UNLOAD_PROBABILITY(server):
    send_200_response(server)

    given_probability = int(server.parsed_url[2])
    if given_probability >= 0 and given_probability <= 100:
        server.wfile.write(f"Probability set to {given_probability}".encode())
    else:
        server.wfile.write(f"speed should be 0-100".encode())

    with data.lock:
        data.unload_probability = given_probability / 100


def post_SET_PNP_CONFIDENCE_LEVEL(server):
    send_200_response(server)

    given_confidence = int(server.parsed_url[2])
    if given_confidence >= 0 and given_confidence <= 100:
        server.wfile.write(f"Confidence set to {given_confidence}".encode())
    else:
        server.wfile.write(f"Confidence should be 0-100".encode())

    with data.lock:
        data.pnp_confidence = given_confidence / 100


def post_CLEAR_STAR_WHEEL_ERROR(server):
    send_200_response(server)
    server.wfile.write("post_CLEAR_STAR_WHEEL_ERROR".encode())
    handler.clear_star_wheel_error()


def post_CLEAR_UNLOADER_ERROR(server):
    send_200_response(server)
    server.wfile.write("CLEAR_UNLOADER_ERROR".encode())
    handler.clear_unloader_error()


def post_MOVE_CW(server):
    send_200_response(server)
    server.wfile.write("MOVE CW".encode())
    handler.move_star_wheel_cw()


def post_MOVE_CCW(server):
    send_200_response(server)
    server.wfile.write("MOVE CCW".encode())
    handler.move_star_wheel_ccw()


def post_CLEAR_UNLOADER_ERROR(server):
    send_200_response(server)
    server.wfile.write("CLEAR_UNLOADER_ERROR".encode())
    handler.clear_unloader_error()


def post_UNLOAD(server):
    send_200_response(server)
    server.wfile.write("UNLOAD".encode())
    handler.unload()


def post_SET_CYCLE_TIME(server):
    send_200_response(server)

    cycle_time = int(server.parsed_url[2])
    if cycle_time >= 0 and cycle_time <= 20:
        server.wfile.write(f"Cycle time set to {cycle_time}".encode())
    else:
        server.wfile.write(f"Cycle time exceed bounds".encode())

    with data.lock:
        data.pnp_data.cycle_time = cycle_time


def post_SET_POS(server):
    send_200_response(server)
    sw_pos = int(server.parsed_url[2])
    with data.lock:
        if sw_pos >= 0 and sw_pos <= 1000:
            data.sw_pos = sw_pos
            server.wfile.write(f"sw position set to {sw_pos}".encode())
        else:
            server.wfile.write(f"sw position exceed bounds".encode())

def post_SAVE_STAR_WHEEL_ZERO(server):
    send_200_response(server)
    with data.lock:
        if not data.dummy_enabled or data.pnp_enabled:
            server.wfile.write(f"Saved the 0 point ".encode())
            handler.save_star_wheel_zero()
            time.sleep(1)
            BscbAPI.BOARD.reboot()

def post_SAVE_STAR_WHEEL_OFFSET(server):
    send_200_response(server)
    with data.lock:
        if not data.dummy_enabled or data.pnp_enabled:
            server.wfile.write(f"Saved Offset to {data.sw_pos} ".encode())
            handler.save_star_wheel_offset()
            time.sleep(1)
            BscbAPI.BOARD.reboot()

def post_MOVE_STAR_WHEEL(server):
    sw_pos = int(server.parsed_url[2])
    send_200_response(server)
    data.sw_pos = sw_pos
    with data.lock:
        if not data.dummy_enabled or data.pnp_enabled:
            server.wfile.write(f"moved SW to {data.sw_pos} ".encode())
            handler.move_star_wheel_to_pos()