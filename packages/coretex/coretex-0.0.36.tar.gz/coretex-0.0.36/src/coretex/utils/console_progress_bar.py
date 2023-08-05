from typing import Final
from threading import Lock

import sys


class ConsoleProgressBar:

    barLength: int = 30

    def __init__(self, total: int, title: str):
        self.total: Final = total
        self.title: Final = title

        self.__current = 0
        self.__lock = Lock()

    def update(self) -> None:
        with self.__lock:
            self.__current += 1

            currentPct = float(self.__current) * 100.0 / self.total
            progressBar = '=' * int(currentPct / 100 * ConsoleProgressBar.barLength - 1) + '>'
            emptySpace = '.' * (ConsoleProgressBar.barLength - len(progressBar))

            sys.stdout.write("\r")
            sys.stdout.write(">> [Coretex] {0}: [{1}{2}] - {3}%".format(self.title, progressBar, emptySpace, int(round(currentPct))))
            sys.stdout.flush()

    def finish(self) -> None:
        with self.__lock:
            currentPct = 100
            progressBar = "=" * int(currentPct / 100 * ConsoleProgressBar.barLength)
            emptySpace = "." * (ConsoleProgressBar.barLength - len(progressBar))

            sys.stdout.write("\r")
            sys.stdout.write(">> [Coretex] {0}: [{1}{2}] - {3}% - {4}\n".format(self.title, progressBar, emptySpace, int(round(currentPct)), "Finished"))
            sys.stdout.flush()
