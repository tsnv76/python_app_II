"""
It is a launcher for starting subprocesses for server and clients of two types: senders and listeners.
for more information:
https://stackoverflow.com/questions/67348716/kill-process-do-not-kill-the-subprocess-and-do-not-close-a-terminal-window
"""

import os
import signal
import subprocess
import sys
from time import sleep

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_subprocess(file_with_args):
    sleep(0.2)
    file_full_path = f"{PYTHON_PATH} {BASE_PATH}/{file_with_args}"
    args = ["gnome-terminal", "--disable-factory", "--", "bash", "-c", file_full_path]
    return subprocess.Popen(args, preexec_fn=os.setpgrp)


process = []
while True:
    TEXT_FOR_INPUT = "Выберите действие: q - выход, s - запустить сервер, k - запустить клиенты, x - закрыть все окна: "
    action = input(TEXT_FOR_INPUT)

    if action == 'q':
        break
    elif action == 's':
        # Запускаем сервер
        process.append(get_subprocess("server.py"))
    elif action == "k":
        num = int(input("Введите количество клиентских приложений: "))
        for i in range(num):
            process.append(get_subprocess(f"client.py -n user{i + 1} -p 123456"))

    elif action == "x":
        while process:
            victim = process.pop()
            os.killpg(victim.pid, signal.SIGINT)
