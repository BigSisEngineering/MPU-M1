import streamlit as st
from datetime import datetime
from enum import Enum
import requests
import time
import ast
import threading

# ------------------------------------------------------------------------------------------------ #
from src import tasks
from src._shared_variables import SV

cage_pos_list = [
    "05",
    "02",
    "04",
    "03",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
]

cage_list = [
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
]

action_list = (
    "star wheel init",
    "unloader init",
    "clear star wheel error",
    "clear unloader error",
    "enable dummy",
    "disable dummy",
    "enable pnp",
    "disable pnp",
)

post_request_dict = {
    "star wheel init": "STAR_WHEEL_INIT",
    "unloader init": "UNLOADER_INIT",
    "clear star wheel error": "CLEAR_STAR_WHEEL_ERROR",
    "clear unloader error": "CLEAR_UNLOADER_ERROR",
    "enable dummy": "ENABLE_DUMMY",
    "disable dummy": "DISABLE_DUMMY",
    "enable pnp": "ENABLE_PNP",
    "disable pnp": "DISABLE_PNP",
}


class Mode(Enum):
    pnp_mode = 0
    dummy_mode = 1
    idle = 2
    offline = 3


class Status(Enum):
    normal = 0
    slot_empty = 1
    error = 2
    offline = 3
    not_init = 4


def get_mode_emoji(mode: Mode):
    if mode == Mode.pnp_mode:
        return "🟢"
    elif mode == Mode.dummy_mode:
        return "🔵"
    elif mode == Mode.idle:
        return "🟡"
    elif mode == Mode.offline:
        return "⚫"


def get_status_emoji(status: Status):
    if status == Status.normal:
        return "🟩"
    elif status == Status.slot_empty:
        return "🟨"
    elif status == Status.error:
        return "🟥"
    elif status == Status.offline:
        return "⬛"
    elif status == Status.not_init:
        return "🟦"


@st.cache_data()
def get_first_init_time():
    return "------"


cage_mode_list = [Mode.offline] * 14
cage_status_list = [Status.offline] * 14


def get_request_for_board_data(url, ctn):
    try:
        response = requests.get(url, timeout=(2, 10)).json()

        sensor_values = ast.literal_eval(response["sensors_values"])
        is_sensor_ok = (sensor_values[0] >= 100) and (sensor_values[2] >= 100)
        if response["star_wheel_status"] == "overload" or response["unloader_status"] == "overload":
            cage_status_list[ctn] = Status.error
        elif response["star_wheel_status"] == "not_init" or response["unloader_status"] == "not_init":
            cage_status_list[ctn] = Status.not_init
        elif not is_sensor_ok:
            cage_status_list[ctn] = Status.slot_empty
        elif (
            response["star_wheel_status"] == "idle"
            or response["star_wheel_status"] == "normal"
            or response["unloader_status"] == "idle"
            or response["unloader_status"] == "normal"
        ):
            cage_status_list[ctn] = Status.normal
        else:
            cage_status_list[ctn] = Status.offline

        mode = response["mode"]
        if mode == "idle":
            cage_mode_list[ctn] = Mode.idle
        elif mode == "pnp":
            cage_mode_list[ctn] = Mode.pnp_mode
        elif mode == "dummy":
            cage_mode_list[ctn] = Mode.dummy_mode
        else:
            cage_mode_list[ctn] = Mode.offline

    except Exception as e:
        print(f"{ctn+2} - The request of {url} - {e}")
        cage_mode_list[ctn] = Mode.offline
        cage_status_list[ctn] = Status.offline


def post_request_to_cage(url):
    try:
        requests.post(url, timeout=0.4)
    except Exception as e:
        pass


def main():
    st.set_page_config(
        page_title=f"Module 1",
        page_icon="🖥️",
        layout="wide",
    )
    # ------------------------------------------------------------------------------------------------ #
    # todo:
    tasks.start()    # !MAKE SURE THIS ONLY STARTS ONCE

    st.title("M1 Control")
    cols = st.columns(4)
    with cols[0]:
        if st.button("Start 1A"):
            SV.w_run(True)

    with cols[1]:
        if st.button("add 10 pots"):
            tasks.a3_task.add_pots(10)
            print("Added 10 pots")

    with cols[2]:
        if st.button("set zero"):
            tasks.a3_task.set_zero()
            print("set zero")
            
    with cols[3]:
        if st.button("Stop 1A"):
            SV.w_run(False)
    # ------------------------------------------------------------------------------------------------ #
    st.divider()
    last_update_time = get_first_init_time()
    if st.button("Update Cages Status"):
        last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ctn = 0
        threads = []
        with st.spinner("Updating"):
            for i in cage_list:
                url = f"http://cage0x00{i}.local:8080/BoardData"
                t = threading.Thread(
                    target=get_request_for_board_data,
                    args=(
                        url,
                        ctn,
                    ),
                )
                threads.append(t)
                t.daemon = True
                t.start()
                ctn = ctn + 1
            for t in threads:
                t.join()

    # -------------------------------------------------------------------------------------------- #
    st.write("If cage is offline, click the cage ID and forward to its page")
    cols = st.columns(3)
    with cols[0]:
        st.write(f"🟢 PnP Mode |  🔵 Dummy Mode  |  🟡 Idle  |  ⚫ offline")
    with cols[1]:
        st.write(f"🟩 Normal  |  🟨 Slot(s) Empty  |  🟥 overload  |  🟦 not init  |  ⬛ offline")
    with cols[2]:
        st.write(f"Last update time: {last_update_time}")
    # ID
    cols = st.columns(14)
    for i in range(0, 14):
        with cols[i]:
            st.write(
                f"""<a href="http://cage0x00{cage_pos_list[i]}:8501">cage{cage_pos_list[i]}</a>""",
                unsafe_allow_html=True,
            )
    # Mode
    cols = st.columns(14)
    for i in range(0, 14):
        with cols[i]:
            pos = int(cage_pos_list[i]) - 2
            st.write(get_mode_emoji(cage_mode_list[pos]))
    # Status
    cols = st.columns(14)
    for i in range(0, 14):
        with cols[i]:
            pos = int(cage_pos_list[i]) - 2
            st.write(get_status_emoji(cage_status_list[pos]))
    # ------------------------------------------------------------------------------------------------ #
    st.divider()
    select_all = st.checkbox("Select all")
    if select_all:
        selected_cages = st.multiselect(
            "Select cage(s)",
            cage_list,
            cage_list,
        )
    else:
        selected_cages = st.multiselect(
            "Select cage(s)",
            cage_list,
        )
    # ------------------------------------------------------------------------------------------------ #
    selected_action = None
    with st.form("my_form"):
        selected_action = st.selectbox("Pick an action", action_list)
        submitted = st.form_submit_button("Execute")
        if submitted:
            with st.spinner("Executing action..."):
                threads = list()
                for cage in selected_cages:
                    url = f"http://cage0x00{cage}.local:8080/{post_request_dict[selected_action]}"
                    t = threading.Thread(target=post_request_to_cage, args=(url,))
                    threads.append(t)
                    t.daemon = True
                    t.start()
                for t in threads:
                    t.join()
    # ------------------------------------------------------------------------------------------------ #

    # -------------------------------------------------------------------------------------------- #
    st.divider()

    # # Apply action here
    # st.write(selected_cages)

    # st.write(selected_action)


if __name__ == "__main__":
    main()
