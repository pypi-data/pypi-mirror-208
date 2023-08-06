from threading import Thread

import time
import logging

from ..coretex import ExecutingExperiment


class Heartbeat(Thread):

    def __init__(self, heartbeatRate: int = 10):
        super(Heartbeat, self).__init__()

        # Don't wait for this thread to finish once the
        # non daemon threads have exited
        self.setDaemon(True)
        self.setName("Heartbeat")

        if heartbeatRate < 1:
            raise ValueError(">> [Coretex] updateInterval must be expressed as an integer of seconds")

        self.__heartbeatRate = heartbeatRate

    def run(self) -> None:
        while True:
            time.sleep(self.__heartbeatRate)

            status = ExecutingExperiment.current().status

            lastStatusMessage = ExecutingExperiment.current().getLastStatusMessage()
            if lastStatusMessage is None:
                continue

            logging.getLogger("coretexpylib").debug(">> [Coretex] Heartbeat")
            ExecutingExperiment.current().updateStatus(status, lastStatusMessage)
