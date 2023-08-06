from typing import Callable, Optional, Type, TypeVar, Tuple, List
from enum import IntEnum

import logging
import sys

from .remote import processRemote
from .local import processLocal
from ..coretex import ExperimentStatus, NetworkDataset, ExecutingExperiment, MetricType
from ..logging import LogHandler, initializeLogger, LogSeverity
from ..networking import RequestFailedError
from ..folder_management import FolderManager


DatasetType = TypeVar("DatasetType", bound = "NetworkDataset")


class ExecutionType(IntEnum):
     # TODO: NYI on backend

     local = 1
     remote = 2


def _prepareForExecution(
     experimentId: int,
     datasetType: Optional[Type[DatasetType]] = None,
     metrics: Optional[List[Tuple[str, str, MetricType, str, MetricType]]] = None
) -> None:
     experiment = ExecutingExperiment.startExecuting(experimentId, datasetType)

     logPath = FolderManager.instance().logs / f"{experimentId}.log"
     customLogHandler = LogHandler.instance()
     customLogHandler.currentExperimentId = experimentId

     # if logLevel exists apply it, otherwise default to info
     severity = LogSeverity.info
     logLevel = experiment.parameters.get("logLevel")

     if logLevel is not None:
          severity = LogSeverity(logLevel)

     initializeLogger(severity, logPath)

     experiment.updateStatus(
          status = ExperimentStatus.inProgress,
          message = "Executing project."
     )

     if metrics is not None:
          experiment.createMetrics(metrics)

          if len(ExecutingExperiment.current().metrics) > 0:
               logging.getLogger("coretexpylib").info(">> [Coretex] Metrics successfully created.")


def initializeProject(
     mainFunction: Callable[[ExecutingExperiment], None],
     datasetType: Optional[Type[DatasetType]] = None,
     metrics: Optional[List[Tuple[str, str, MetricType, str, MetricType]]] = None
) -> None:
     """
          Initializes and starts the python project as
          Coretex experiment

          Parameters
          ----------
          mainFunction : Callable[[ExecutingExperiment], None]
               entry point function
          datasetType : Optional[Type[DatasetType]]
               Custom dataset if there is any (Not required)
          metrics : Optional[List[Tuple[str, str, MetricType, str, MetricType]]]
               list of metrics that will be created for executing Experiment
     """

     try:
          experimentId, callback = processRemote()
     except:
          experimentId, callback = processLocal()

     try:
          _prepareForExecution(experimentId, datasetType, metrics)

          callback.onStart()

          logging.getLogger("coretexpylib").info("Experiment execution started")
          mainFunction(ExecutingExperiment.current())

          callback.onSuccess()
     except RequestFailedError:
          callback.onNetworkConnectionLost()
     except KeyboardInterrupt:
          callback.onKeyboardInterrupt()
     except BaseException as ex:
          callback.onException(ex)

          # sys.exit is ok here, finally block is guaranteed to execute
          # due to how sys.exit is implemented (it internally raises SystemExit exception)
          sys.exit(1)
     finally:
          callback.onCleanUp()
