from typing import Final
from typing_extensions import Self

import sys
import logging
import multiprocessing

from ..coretex import Experiment
from ..folder_management import FolderManager
from ..logging import LogHandler

from .calculate_metrics import uploadMetricsWorker


class ProjectCallback:

    def __init__(self, experiment: Experiment, refreshToken: str) -> None:
        self._experiment: Final = experiment

        self.__outputStream, self.__inputStream = multiprocessing.Pipe()

        self.process = multiprocessing.Process(
            target = uploadMetricsWorker,
            args = (self.__outputStream, refreshToken, self._experiment.id)
        )

    @classmethod
    def create(cls, experimentId: int, refreshToken: str) -> Self:
        experiment = Experiment.fetchById(experimentId)
        if experiment is None:
            raise ValueError

        return cls(experiment, refreshToken)

    def onStart(self) -> None:
        self.process.start()

        result = self.__inputStream.recv()
        if result["code"] != 0:
            raise RuntimeError(result["message"])

        logging.getLogger("coretexpylib").info(result["message"])

    def onSuccess(self) -> None:
        pass

    def onKeyboardInterrupt(self) -> None:
        pass

    def onException(self, exception: BaseException) -> None:
        logging.getLogger("coretexpylib").debug(exception, exc_info = True)
        logging.getLogger("coretexpylib").critical(str(exception))

    def onNetworkConnectionLost(self) -> None:
        FolderManager.instance().clearTempFiles()

        sys.exit(1)

    def onCleanUp(self) -> None:
        logging.getLogger("coretexpylib").info("Experiment execution finished")
        self.process.kill()

        try:
            from py3nvml import py3nvml
            py3nvml.nvmlShutdown()
        except:
            pass

        LogHandler.instance().flushLogs()
        LogHandler.instance().reset()

        FolderManager.instance().clearTempFiles()
