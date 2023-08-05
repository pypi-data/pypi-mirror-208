from typing import Tuple, Optional
from getpass import getpass

import logging
import os

from tap import Tap

import psutil

from .heartbeat import Heartbeat
from .base import ProjectCallback
from ..coretex import Experiment, ExperimentStatus
from ..folder_management import FolderManager
from ..networking import NetworkManager
from ..coretex.experiment.parameters import ExperimentParameter


class LocalProjectCallback(ProjectCallback):

    def onStart(self) -> None:
        super().onStart()

        FolderManager.instance().clearTempFiles()

        logging.getLogger("coretexpylib").info("Heartbeat started")

        heartbeat = Heartbeat()
        heartbeat.start()

    def onSuccess(self) -> None:
        super().onSuccess()

        self._experiment.updateStatus(ExperimentStatus.completedWithSuccess)

    def onKeyboardInterrupt(self) -> None:
        super().onKeyboardInterrupt()

        logging.getLogger("coretexpylib").info(">> [Coretex] Stopping the experiment")

        self._experiment.updateStatus(ExperimentStatus.stopping)

        experimentProcess = psutil.Process(os.getpid())
        children = experimentProcess.children(recursive = True)

        logging.getLogger("coretexpylib").debug(f">> [Coretex] Number of child processes: {len(children)}")

        for process in children:
            process.kill()

        for process in children:
            process.wait()

        self._experiment.updateStatus(ExperimentStatus.stopped)

    def onException(self, exception: BaseException) -> None:
        super().onException(exception)

        self._experiment.updateStatus(ExperimentStatus.completedWithError)


class LocalArgumentParser(Tap):

    username: Optional[str]
    password: Optional[str]

    projectId: int
    name: Optional[str]
    description: Optional[str]

    def configure(self) -> None:
        self.add_argument("--username", nargs = "?", type = str, default = None)
        self.add_argument("--password", nargs = "?", type = str, default = None)

        self.add_argument("--projectId", type = int)
        self.add_argument("--name", nargs = "?", type = str, default = None)
        self.add_argument("--description", nargs = "?", type = str, default = None)


def processLocal() -> Tuple[int, ProjectCallback]:
    parser = LocalArgumentParser().parse_args()
    networkManager = NetworkManager.instance()

    if parser.username is not None and parser.password is not None:
        logging.getLogger("coretexpylib").info(">> [Coretex] Logging in with provided credentials")
        response = networkManager.authenticate(parser.username, parser.password)
    elif networkManager.hasStoredCredentials:
        logging.getLogger("coretexpylib").info(">> [Coretex] Logging in with stored credentials")
        response = networkManager.authenticateWithStoredCredentials()
    else:
        logging.getLogger("coretexpylib").info(">> [Coretex] Credentials not provided/stored")

        username = input("Enter your username: ")
        password = getpass("Enter your password: ")

        response = networkManager.authenticate(username, password)

    if response.hasFailed():
        raise RuntimeError(">> [Coretex] Failed to authenticate")

    if not os.path.exists("experiment.config"):
        raise FileNotFoundError(">> [Coretex] \"experiment.config\" file not found")

    parameters = ExperimentParameter.readExperimentConfig()

    experiment = Experiment.startCustomExperiment(
        parser.projectId,
        # Dummy Local node ID, hardcoded as it is only a temporary solution,
        # backend will add a new ExperimentType (local) which does not require a specific
        # node to run
        43,
        parser.name,
        parser.description,
        parameters = [parameter.encode() for parameter in parameters]
    )

    experiment.updateStatus(ExperimentStatus.preparingToStart)

    return experiment.id, LocalProjectCallback(experiment, response.json["refresh_token"])
