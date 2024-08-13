import threading
from typing import Dict, Callable, List

# ------------------------------------------------------------------------------------ #
from src import components

# ------------------------------------------------------------------------------------ #
from src._shared_variables import Cages

class Operation:
    executing_cage_command = False
    results = {}

    @staticmethod
    def _worker_thread(func: Callable, key: str) -> None:
        """Worker thread function that executes the provided function and stores the result."""
        Operation.results[key] = func()

    @staticmethod
    def manage_cage_actions(data) -> str:
        """
        Manages the execution of cage actions based on a boolean list.

        :param bool_list: A list of booleans indicating which cages should execute the action.
        :param action: The action to execute on the selected cages.
        :return: A string summary of the execution results.
        """
        try:
            bool_list: List[bool] = data["bool_list"]
            action: str = data["action"]

            if not Operation.executing_cage_command:
                Operation.executing_cage_command = True

                worker_dict: Dict[str, Callable] = {}

                # Create worker functions based on the bool_list
                for index, exec_bool in enumerate(bool_list):
                    if exec_bool:
                        cage_number = f"00{index + 1:02d}"
                        for cage in Cages:
                            if cage_number in cage.value:
                                function = lambda c=cage: components.cage_dict[c].exec_action(action)
                                worker_dict[f"cage{index + 1:02d}"] = function
                                break

                # Start threads for each cage action
                threads: List[threading.Thread] = []
                for key, func in worker_dict.items():
                    thread = threading.Thread(target=Operation._worker_thread, args=(func, key))
                    threads.append(thread)

                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                # Collect and format the results
                results: str = f"Execute {action}\n"
                for key in worker_dict.keys():
                    results += f"{key}: {Operation.results.get(key, 'No result')}\n"

                # Reset the operation state
                Operation.executing_cage_command = False
                Operation.results = {}
                return results.strip()

            return "Another cage command is already executing. Please wait."

        except Exception as e:
            return f"{e}"
