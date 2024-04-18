from src.tasks import a1, a2, a3, c1, c2, c3


# -------------------------------------------------------- #
from src._shared_variables import SV

print_name = "TASK"

a1_task = a1.A1()
a2_task = a2.A2()
a3_task = a3.A3()
c1_task = c1.C1()
c2_task = c2.C2()
c3_task = c3.C3()


a1_task.start()
a2_task.start()
a3_task.start()


# -------------------------------------------------------- #
# def start():
#     if not SV.THREAD_STARTED:
#         SV.THREAD_STARTED = True
#         # c1_task.start() # ! temp comment for Amit's testing
#         # c2_task.start()
#         # c3_task.start()
#         print("{:^10} Start.".format(print_name))
