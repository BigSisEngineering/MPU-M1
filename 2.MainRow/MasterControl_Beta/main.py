import streamlit as st
import threading
import time
from datetime import datetime

# ------------------------------------------------------------------------------------------------ #
from src import tasks, components

# -------------------------------------------------------- #
from src.streamlit_server.content_generator import PlaceholderID, content

# -------------------------------------------------------- #
from src._shared_variables import SV, Cages


print("safe to load")

cage_pos_list = [
    "01",
    "05",
    "02",
    "03",
    "04",
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
    "01",
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
    "restart software",
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
    "restart software": "RESTART",
}


def main():
    # placeholder = {}

    st.set_page_config(
        page_title=f"Module 1",
        page_icon="🖥️",
        layout="wide",
    )

    # ------------------------------------------------------------------------------------------------ #
    st.title("M1 Control")
    cols = st.columns(6)
    with cols[0]:
        if st.button("Start 1A"):
            SV.w_run_1a(True)

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
            SV.w_run_1a(False)

    with cols[4]:
        if st.button("Start 1C"):
            # st.write("nope.")
            SV.w_run_1c(True)

    with cols[5]:
        if st.button("Stop 1C"):
            SV.w_run_1c(False)

    # ------------------------------------------------------------------------------------------------ #
    st.divider()
    st.write("1A Query")

    if st.button("Show"):
        cols = st.columns(3)
        with cols[0]:
            st.write("Should the Pot Sorter transfer belt be running?")
            # placeholder[PlaceholderID.query_1a_pot_sorter] = st.empty()
            # with placeholder[PlaceholderID.query_1a_pot_sorter].container():
            # st.write("Loading...")
            st.write(content.r_content(PlaceholderID.query_1a_pot_sorter))

        with cols[1]:
            st.write("Should the Diet Dispenser be dispensing?")
            # placeholder[PlaceholderID.query_1a_diet_dispenser] = st.empty()
            # with placeholder[PlaceholderID.query_1a_diet_dispenser].container():
            # st.write("Loading...")
            st.write(content.r_content(PlaceholderID.query_1a_diet_dispenser))

        with cols[2]:
            st.write("Should the Pot Dispenser be dispensing?")
            # placeholder[PlaceholderID.query_1a_pot_dispenser] = st.empty()
            # with placeholder[PlaceholderID.query_1a_pot_dispenser].container():
            # st.write("Loading...")
            st.write(content.r_content(PlaceholderID.query_1a_pot_dispenser))

    # ------------------------------------------------------------------------------------------------ #
    st.divider()
    st.write("1C Query")
    cols = st.columns(3)
    with cols[0]:
        st.write("N/A")
        # placeholder[PlaceholderID.query_1c_chimney_sorter] = st.empty()
    with cols[1]:
        st.write("N/A")
        # placeholder[PlaceholderID.query_1c_channelizer] = st.empty()
    with cols[2]:
        st.write("N/A")
        # placeholder[PlaceholderID.query_1c_chimney_placer] = st.empty()

    # ------------------------------------------------------------------------------------------------ #
    st.divider()

    if st.button("Update Status"):
        with st.spinner("Updating..."):
            SV.last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.write("If cage is offline, click the cage ID and forward to its page")
    cols = st.columns(3)
    with cols[0]:
        st.write(f"🟢 PnP Mode |  🔵 Dummy Mode  |  🟡 Idle  |  ⚫ offline")
    with cols[1]:
        st.write(
            f"🟩 Normal  |  🟨 Slot(s) Empty  |  🟥 overload  |  🟦 not init  |  ⬛ offline"
        )
    with cols[2]:
        st.write(f"Last update time: {SV.last_update_time}")

    # ID
    cols_id = st.columns(15)
    for i in range(0, 15):
        with cols_id[i]:
            st.write(
                f"""<a href="http://cage0x00{cage_pos_list[i]}:8501">cage{cage_pos_list[i]}</a>""",
                unsafe_allow_html=True,
            )

    # Mode
    cols_mode = st.columns(15)

    for cage in Cages:
        cage_number = cage.name[-2:]
        for i, _cage in enumerate(cage_pos_list):
            if _cage in cage.name:
                with cols_mode[i]:
                    for id in PlaceholderID:
                        if "mode" in id.name and cage_number in id.name:
                            # placeholder[id] = st.empty()
                            # with placeholder[id].container():
                            # st.write("⚫")
                            st.write(content.r_content(id))
                            break

    # status
    cols_status = st.columns(15)

    for cage in Cages:
        cage_number = cage.name[-2:]
        for i, _cage in enumerate(cage_pos_list):
            if _cage in cage.name:
                with cols_status[i]:
                    for id in PlaceholderID:
                        if "status" in id.name and cage_number in id.name:
                            # placeholder[id] = st.empty()
                            # with placeholder[id].container():
                            # st.write("⬛")
                            st.write(content.r_content(id))
                            break

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
                for cage in Cages:
                    for _cage in selected_cages:
                        if _cage in cage.name:
                            t = threading.Thread(
                                target=components.cage_dict[cage].execute_action,
                                args=(post_request_dict[selected_action],),
                            )
                            threads.append(t)
                            t.daemon = True
                            t.start()

                for t in threads:
                    t.join()
    # ------------------------------------------------------------------------------------------------ #

    # -------------------------------------------------------------------------------------------- #
    st.divider()

    # time_stamp = 0

    # while True:

    #     if time.time() - time_stamp > 2:

    #         for id in PlaceholderID:
    #             placeholder[id].empty()
    #             with placeholder[id].container():
    #                 st.write(content.r_content(id))

    #         time_stamp = time.time()
    # time.sleep(5)


if __name__ == "__main__":
    main()
