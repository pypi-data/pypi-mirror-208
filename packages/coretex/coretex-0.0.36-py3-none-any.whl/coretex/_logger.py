from datetime import datetime

from .folder_management import FolderManager
from .logging import LogSeverity, initializeLogger
from .utils import DATE_FORMAT


def _initializeDefaultLogger() -> None:
    logPath = FolderManager.instance().logs / f"{datetime.now().strftime(DATE_FORMAT)}.log"
    initializeLogger(LogSeverity.info, logPath)
