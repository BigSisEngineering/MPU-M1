# from flask import Blueprint, request, jsonify
# from src import tasks, components
# from src._shared_variables import SV, Cages

# import threading
# from typing import List, Callable, Dict
# import time

# # ------------------------------------------------------------------------------------------------ #
# from src.components import A2, A3
# from src import components

# blueprint = Blueprint('post_handler', __name__)

# _active_threads = {}

# def _exec_function(func, args=None):
#     function_name = func.__name__
#     execute = False
#     print(f"Checking {function_name}")
    
#     if args is not None:
#         if not isinstance(args, tuple):
#             args = (args,)
    
#     if function_name not in _active_threads or not _active_threads[function_name].is_alive():
#         execute = True
#         _active_threads.pop(function_name, None)
    
#     print(f"Execute {function_name}: {execute}")
#     if execute:
#         thread = threading.Thread(target=func, args=args if args else ())
#         _active_threads[function_name] = thread
#         thread.start()
#         print(f"Started {function_name}")
#     else:
#         print(f"Execution blocked: {function_name} is already executing.")

# @blueprint.route('/1A_1C', methods=['POST'])
# def handle_post():
#     try:
#         data = request.get_json()
#         if data is None:
#             print("No data received, or Content-Type may not be set to application/json.")
#             return jsonify({"status": "error", "message": "No data received"}), 400
#         print("Received data:", data)
#         handle_1A_1C(data)
#         return jsonify({"status": "success"})
#     except Exception as e:
#         print(f"Error handling 1A_1C post: {e}")
#         return jsonify({"status": "error", "message": str(e)}), 500

# def handle_1A_1C(data):
#     # Process the received data
#     SV.is1AActive = data.get("is1AActive", False)
#     SV.is1CActive = data.get("is1CActive", False)

#     # Check for toggles and execute associated tasks
#     if data.get("addTen", False):
#         # tasks.a3_task.add_pots(10)
#         _exec_function(tasks.a3_task.add_pots, 10)
#     if data.get("setZero", False):
#         # tasks.a3_task.set_zero()
#         _exec_function(tasks.a3_task.set_zero)

#     if data.get("raiseNozzle", False):
#         # A2.raise_nozzle()
#         _exec_function(A2.raise_nozzle)
#     if data.get("lowerNozzle", False):
#         # A2.reposition_nozzle()
#         _exec_function(A2.reposition_nozzle)
#     if data.get("clearErrorSW2", False):
#         # A2.sw_ack_fault()
#         _exec_function(A2.sw_ack_fault)
#     if data.get("homeSW2", False):
#         # A2.sw_home()
#         _exec_function(A2.sw_home)
    
#     if data.get("clearErrorSW3", False):
#         # A3.sw_ack_fault()
#         _exec_function(A3.sw_ack_fault)
#     if data.get("homeSW3", False):
#         # A3.sw_home()
#         _exec_function(A3.sw_home)

#     # Reset toggles immediately after processing
#     data["addTen"] = False
#     data["setZero"] = False

#     data["raiseNozzle"] = False
#     data["lowerNozzle"] = False
#     data["clearErrorSW2"] = False
#     data["homeSW2"] = False

#     data["clearErrorSW3"] = False
#     data["homeSW3"] = False

   

# @blueprint.route('/1B', methods=['POST'])
# def execute_cages_action():
#     data = request.json()
#     results = get_cages_action(data.get("cages", []), data.get("action", ""))
#     return jsonify(results)

# def get_cages_action(cages: List, action: str):
#     for cage_id in cages:
#         for cage in Cages:
#             if cage_id == cage.value:
#                 threading.Thread(target=components.cage_dict[cage].exec_action, args=(action,)).start()


# def variables_1a_1c():
#     while True:
#         print(f"Current States -> is1AActive: {SV.is1AActive}, is1CActive: {SV.is1CActive}")
#         SV.w_run_1a(SV.is1AActive)
#         SV.w_run_1c(SV.is1CActive)
#         time.sleep(3)


# threading.Thread(target=variables_1a_1c).start()




from flask import Blueprint, request, jsonify
from src import tasks, components
from src._shared_variables import SV, Cages
from src.components import A2, A3
import threading
import time
import logging

blueprint = Blueprint('post_handler', __name__)
logger = logging.getLogger(__name__)

_active_threads = {}


def exec_function(func, args=None):
    function_name = func.__name__
    if function_name not in _active_threads or not _active_threads[function_name].is_alive():
        print(f"Executing {function_name}")
        if args is not None:
            if not isinstance(args, tuple):
                args = (args,)  # Ensure args is a tuple even if it's a single value
        else:
            args = ()
        thread = threading.Thread(target=func, args=args)
        _active_threads[function_name] = thread
        thread.start()
    else:
        print(f"Execution blocked: {function_name} is already executing.")



@blueprint.route('/1A_1C', methods=['POST'])
def handle_1A_1C_post():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    logger.info("Received data for 1A_1C: {}".format(data))
    handle_1A1C_state_changes(data)
    handle_1A1C_actions(data)
    reset_action_flags(data)
    return jsonify({"status": "success"})

def handle_1A1C_state_changes(data):
    SV.is1AActive = data.get("is1AActive", False)
    SV.is1CActive = data.get("is1CActive", False)

def handle_1A1C_actions(data):
    actions = {
        "addTen": (tasks.a3_task.add_pots, 10),
        "setZero": (tasks.a3_task.set_zero, None),
        "raiseNozzle": (A2.raise_nozzle, None),
        "lowerNozzle": (A2.reposition_nozzle, None),
        "clearErrorSW2": (A2.sw_ack_fault, None),
        "homeSW2": (A2.sw_home, None),
        "clearErrorSW3": (A3.sw_ack_fault, None),
        "homeSW3": (A3.sw_home, None)
    }
    for action, (func, arg) in actions.items():
        if data.get(action, False):
            exec_function(func, arg)

def reset_action_flags(data):
    for action in ["addTen", "setZero", "raiseNozzle", "lowerNozzle", "clearErrorSW2", "homeSW2", "clearErrorSW3", "homeSW3"]:
        data[action] = False

@blueprint.route('/1B', methods=['POST'])
def execute_cages_action():
    data = request.get_json()
    results = manage_cage_actions(data.get("cages", []), data.get("action", ""))
    return jsonify(results)

def manage_cage_actions(cages, action):
    results = []
    for cage_id in cages:
        for cage in Cages:
            if cage_id == cage.value:
                thread = threading.Thread(target=components.cage_dict[cage].exec_action, args=(action,))
                thread.start()
                results.append(f"Action {action} started for cage {cage_id}")
    return results

def monitor_1A1C_states():
    while True:
        print(f"Monitoring states: is1AActive={SV.is1AActive}, is1CActive={SV.is1CActive}")
        SV.w_run_1a(SV.is1AActive)
        SV.w_run_1c(SV.is1CActive)
        time.sleep(3)

threading.Thread(target=monitor_1A1C_states).start()
