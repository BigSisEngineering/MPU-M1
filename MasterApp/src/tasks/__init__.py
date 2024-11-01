import threading

# -------------------------------------------------------- #
from src.tasks import a1, a2, a3, c1, c2, cage_score


print_name = "TASK"

a1_task = a1.A1()
a2_task = a2.A2()
a3_task = a3.A3()
c1_task = c1.C1()
c2_task = c2.C2()
cage_score_task = cage_score.CageScore()


def _init():
    a1_task.start()
    a2_task.start()
    a3_task.start()
    c1_task.start()
    c2_task.start()
    cage_score_task.start()


def start():
    threading.Thread(target=_init).start()
