from src.tasks import a1, a2, a3

# -------------------------------------------------------- #
from src._shared_variables import SV

print_name = "TASK"

a1_task = a1.A1()
a2_task = a2.A2()
a3_task = a3.A3()


def start():
    if not SV.TASK_THREAD_STARTED:
        SV.TASK_THREAD_STARTED = True
        a1_task.start()
        a2_task.start()
        a3_task.start()
        print("{:^10} Start.".format(print_name))
