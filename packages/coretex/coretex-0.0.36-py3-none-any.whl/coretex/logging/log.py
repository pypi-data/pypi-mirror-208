from typing import Final, Dict
from typing_extensions import Self

import time
import termcolor

from .log_severity import LogSeverity
from ..utils import mathematicalRound
from ..codable import Codable, KeyDescriptor


class Log(Codable):

    """
        Represents a single Coretex console log

        timestamps : float
            timestamp of the log
        message : str
            message of the log
        severity : LogSeverity
            severity of the log
    """

    timestamp: float
    message: str
    severity: LogSeverity

    def __init__(self) -> None:
        super().__init__()

        # type is deprecated, leaving this here until backend no longer requires it
        self.type: Final = 1

    @classmethod
    def _keyDescriptors(cls) -> Dict[str, KeyDescriptor]:
        descriptors = super()._keyDescriptors()

        descriptors["message"] = KeyDescriptor("content")
        descriptors["severity"] = KeyDescriptor(pythonType = LogSeverity)

        return descriptors

    @classmethod
    def create(cls, message: str, severity: LogSeverity) -> Self:
        """
            Creates a new Log object with the current timestamp

            Parameters
            ----------
            message : str
                message of the log
            severity : LogSeverity
                severity of the log

            Returns
            -------
            Self -> Log object
        """

        log = cls()

        log.timestamp = mathematicalRound(time.time(), 6)
        log.message = Log.__createMessage(message, severity)
        log.severity = severity

        return log

    @staticmethod
    def __createMessage(message: str, severity: LogSeverity) -> str:
        message = f"{severity.prefix}: {message}"
        message = termcolor.colored(message, severity.color)

        return message
