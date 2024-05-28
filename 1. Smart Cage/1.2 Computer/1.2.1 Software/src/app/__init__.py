import streamlit as st
from typing import Dict

# ------------------------------------------------------------------------------------------------ #
from src import setup, data, comm, BscbAPI

from src.app import handler, widgets
from src.tasks import camera

from src import CLI
from src.CLI import Level

counter: int = 0
placeholders: Dict[str, st.empty] = dict()
progress_bar: st.progress = None
indicators: Dict[str, widgets.ColourStatusLight] = {
    "star_wheel": widgets.ColourStatusLight("Star Wheel"),
    "buffer": widgets.ColourStatusLight("Sensor-Buffer"),
    "mode": widgets.ColourStatusLight("Mode"),
    "load": widgets.ColourStatusLight("Sensor-Load"),
    "unloader": widgets.ColourStatusLight("Unloader"),
}


def logout():
    global placeholders
    with placeholders["main"].container():
        st.error("You are logged out, Please refresh")
        st.error("You are logged out, Please refresh")
        st.error("You are logged out, Please refresh")
        st.error("You are logged out, Please refresh")
        st.error("You are logged out, Please refresh")
        st.error("You are logged out, Please refresh")
        st.error("You are logged out, Please refresh")
        st.error("You are logged out, Please refresh")
        st.error("You are logged out, Please refresh")


def write():
    global placeholders, progress_bar
    placeholders["main"] = st.empty()
    with placeholders["main"].container():
        page_tittle: str = (
            "## Cage Controller" if setup.CAGE_ID is None else f"## Cage Controller ```ID: {setup.CAGE_ID}```"
        )
        st.markdown(page_tittle)
        # ---------------------------------------------------------------------------------------- #
        cols = st.columns(3)
        with cols[0]:
            st.write(f"version: {setup.SOFTWARE_VERSION}")
        with cols[1]:
            progress_bar = st.progress(0)
        with cols[2]:
            st.button("⟳")
        # ---------------------------------------------------------------------------------------- #
        create_sliders()
        create_status_buttons()
        create_control_buttons()
        placeholders["data"] = st.empty()
        cols = st.columns(5)
        with cols[0]:
            placeholders["indicator_0"] = st.empty()
        with cols[1]:
            placeholders["indicator_1"] = st.empty()
        with cols[2]:
            placeholders["indicator_2"] = st.empty()
        with cols[3]:
            placeholders["indicator_3"] = st.empty()
        with cols[4]:
            placeholders["indicator_4"] = st.empty()
        with st.columns(3)[1]:
            placeholders["img"] = st.empty()


@comm.timing_decorator(interval_s=0.1)
def update(is_new_run: bool):
    global counter, progress_bar, indicators
    # ======================================== Params ======================================== #

    if progress_bar is not None:
        progress_bar.progress(counter)
    with placeholders["data"].container():
        st.write(counter)
        counter = (counter + 1) % 100
    # ==================================== Indicators ==================================== #
    if BscbAPI.lock.acquire(timeout=0.2):
        board_data = BscbAPI.BOARD_DATA
        BscbAPI.lock.release()

    if board_data.star_wheel_status == "overload" or board_data.star_wheel_status == "error":
        indicators["star_wheel"].set_red()
    elif board_data.star_wheel_status == "not_init":
        indicators["star_wheel"].set_yellow()
    elif board_data.star_wheel_status == "idle" or board_data.star_wheel_status == "normal":
        indicators["star_wheel"].set_black()

    if board_data.unloader_status == "overload" or board_data.unloader_status == "error":
        indicators["unloader"].set_red()
    elif board_data.unloader_status == "not_init":
        indicators["unloader"].set_yellow()
    elif board_data.unloader_status == "idle" or board_data.unloader_status == "normal":
        indicators["unloader"].set_black()

    if BscbAPI.BOARD.resolve_sensor_status(board_data.sensors_values, BscbAPI.SensorID.BUFFER.value) == 1:
        indicators["buffer"].set_green()
    else:
        indicators["buffer"].set_black()
    if BscbAPI.BOARD.resolve_sensor_status(board_data.sensors_values, BscbAPI.SensorID.LOAD.value) == 1:
        indicators["load"].set_green()
    else:
        indicators["load"].set_black()

    with placeholders["indicator_0"].container():
        st.markdown(indicators["star_wheel"].display(), unsafe_allow_html=True)
    with placeholders["indicator_1"].container():
        st.markdown(indicators["buffer"].display(), unsafe_allow_html=True)
    with placeholders["indicator_2"].container():
        st.markdown(indicators["mode"].display(), unsafe_allow_html=True)
    with placeholders["indicator_3"].container():
        st.markdown(indicators["load"].display(), unsafe_allow_html=True)
    with placeholders["indicator_4"].container():
        st.markdown(indicators["unloader"].display(), unsafe_allow_html=True)


def play_frame():
    # ====================================== Camera ====================================== #
    img = camera.CAMERA.get_frame()
    if img is not None:
        with placeholders["img"].container():
            st.image(
                img,
                channels="BGR",
                use_column_width=True,
            )


# ------------------------------------------------------------------------------------------------ #
def create_sliders():
    cols = st.columns(3)
    with cols[0]:
        if data.lock.acquire(timeout=1):
            current_ms = data.star_wheel_duration_ms
            data.lock.release()
        else:
            current_ms = 600
        new_ms = st.slider(
            "Star wheel duration (ms)",
            min_value=600,
            max_value=5000,
            value=current_ms,
            step=100,
        )
        if data.lock.acquire(timeout=1):
            data.star_wheel_duration_ms = new_ms
            data.lock.release()

    with cols[1]:
        if data.lock.acquire(timeout=1):
            current_confidence = data.pnp_confidence
            data.lock.release()
        else:
            current_confidence = 1.0
        new_confidence = st.slider(
            "P&P Confidence",
            min_value=0.0,
            max_value=1.0,
            value=current_confidence,
            step=0.1,
        )
        if data.lock.acquire(timeout=1):
            data.pnp_confidence = new_confidence
            data.lock.release()

    with cols[2]:
        if data.lock.acquire(timeout=1):
            current_unload_probability = data.unload_probability
            data.lock.release()
        else:
            current_unload_probability = 1.0
        new_unload_probability = st.slider(
            "Unload Probability",
            min_value=0.0,
            max_value=1.0,
            value=current_unload_probability,
            step=0.1,
        )
        if data.lock.acquire(timeout=1):
            data.unload_probability = new_unload_probability
            data.lock.release()


def create_status_buttons():
    cols = st.columns(6)
    with cols[0]:
        st.button(f"Clear SW Error", use_container_width=True, on_click=handler.clear_star_wheel_error)
    with cols[1]:
        st.button("Star Wheel Init", use_container_width=True, on_click=handler.init_star_wheel)
    with cols[2]:
        st.button("Enable P&P 🟢", use_container_width=True, on_click=handler.enable_pnp)
    with cols[3]:
        st.button("Enable Dummy 🔵", use_container_width=True, on_click=handler.enable_dummy)
    with cols[4]:
        st.button("Unloader Init", use_container_width=True, on_click=handler.init_unloader)
    with cols[5]:
        st.button("Clear UL Error", use_container_width=True, on_click=handler.clear_unloader_error)


def create_control_buttons():
    cols = st.columns(3)
    with cols[0]:
        st.button("↪️", use_container_width=True, on_click=handler.move_star_wheel_ccw)
    with cols[1]:
        st.button("⤵️", use_container_width=True, on_click=handler.unload)
    with cols[2]:
        st.button("↩️", use_container_width=True, on_click=handler.move_star_wheel_cw)
