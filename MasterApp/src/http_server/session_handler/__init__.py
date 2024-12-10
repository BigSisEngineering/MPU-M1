import threading
from flask_socketio import SocketIO
from typing import List, Dict

# ------------------------------------------------------------------------------------ #
from src import components, tasks
from src._shared_variables import SV
from src import setup

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "SESSION"


class Readback:
    M1A = 0
    M1C = 1
    CAGES = 2
    SYSTEM = 3
    INFO = 4
    EXPERIMENT = 5
    SESSION_ACTIVE = 6
    SESSION_END = 7
    CAGE_SCORE = 8


def get_readback_dict(readback: Readback) -> Dict:
    if readback == Readback.M1A:
        return tasks.generate_m1a_dict(raw_dict=True)
    elif readback == Readback.M1C:
        return tasks.generate_m1c_dict(raw_dict=True)
    elif readback == Readback.CAGES:
        return components.generate_cage_dict(raw_dict=True)
    elif readback == Readback.SYSTEM:
        return SV.system_status_raw
    elif readback == Readback.INFO:
        return setup.get_setup_info(raw_dict=True)
    elif readback == Readback.EXPERIMENT:
        return components.generate_cage_experiment_dict(raw_dict=True)
    elif readback == Readback.SESSION_ACTIVE:
        return {"session_timeout": False}
    elif readback == Readback.SESSION_END:
        return {"session_timeout": True}
    elif readback == Readback.CAGE_SCORE:
        return tasks.CAGE_SCORE.get_cage_score(raw_dict=True)


def get_readback_event(readback: Readback) -> str:
    if readback == Readback.M1A:
        return "m1a"
    elif readback == Readback.M1C:
        return "m1c"
    elif readback == Readback.CAGES:
        return "cages"
    elif readback == Readback.SYSTEM:
        return "system"
    elif readback == Readback.INFO:
        return "info"
    elif readback == Readback.EXPERIMENT:
        return "experiment"
    elif readback == Readback.SESSION_ACTIVE:
        return "session"
    elif readback == Readback.SESSION_END:
        return "session"
    elif readback == Readback.CAGE_SCORE:
        return "cage_score"


class Session:
    MAX_SESSIONS: int = 4
    TRANSMIT_DELAY = 1

    active_sessions: List[str] = []
    end_session_event: Dict[str, threading.Event] = {}

    def __init__(self, socketio: SocketIO) -> None:
        self.socketio = socketio

    def __emit(self, readback: Readback, sid) -> None:
        self.socketio.emit(get_readback_event(readback), get_readback_dict(readback), to=sid)

    def __transmission_thread(self, sid: str):
        # init
        while not Session.end_session_event[sid].is_set():
            # todo: only emit experiment status when requested
            self.__emit(Readback.SESSION_ACTIVE, sid)
            self.__emit(Readback.INFO, sid)
            self.__emit(Readback.M1A, sid)
            self.__emit(Readback.M1C, sid)
            self.__emit(Readback.EXPERIMENT, sid)
            self.__emit(Readback.SYSTEM, sid)
            self.__emit(Readback.CAGES, sid)
            self.__emit(Readback.CAGE_SCORE, sid)
            self.socketio.sleep(Session.TRANSMIT_DELAY)

        self.__emit(Readback.SESSION_END, sid)

        # remove session event
        if sid in Session.active_sessions:
            Session.active_sessions.remove(sid)
            Session.end_session_event.pop(sid)
            CLI.printline(Level.DEBUG, "({:^10}) End session -> {}".format(print_name, sid))
        else:
            CLI.printline(Level.ERROR, "({:^10}) Session Key not found! -> {}".format(print_name, sid))

    def create_session(self, sid: str):
        if len(Session.active_sessions) >= Session.MAX_SESSIONS:
            # end oldest session
            sid_pop = Session.active_sessions[0]
            Session.end_session_event[sid_pop].set()

        # create new session
        Session.active_sessions.append(sid)
        Session.end_session_event[sid] = threading.Event()
        threading.Thread(target=self.__transmission_thread, args=(sid,)).start()
        CLI.printline(Level.DEBUG, "({:^10}) Create session -> {}".format(print_name, sid))

    def end_session(self, sid: str):
        # set end session event
        if sid in Session.active_sessions:
            Session.end_session_event[sid].set()
