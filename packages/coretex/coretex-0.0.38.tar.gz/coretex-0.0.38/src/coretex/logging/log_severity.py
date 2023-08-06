from __future__ import annotations

from enum import IntEnum

import logging

class LogSeverity(IntEnum):

    """
        List of all log severities supported by Coretex
    """

    fatal   = 1  # color = red
    error   = 2  # color = red
    warning = 3  # color = yellow
    info    = 4  # color = white
    debug   = 5  # color = yellow

    @property
    def color(self) -> str:
        """
            Color of the log severity

            Returns
            -------
            str -> color
        """

        if self == LogSeverity.fatal:
            return "red"

        if self == LogSeverity.error:
            return "red"

        if self == LogSeverity.warning:
            return "yellow"

        if self == LogSeverity.info:
            return "white"

        if self == LogSeverity.debug:
            return "yellow"

        raise RuntimeError(">> [Coretex] Invalid enum value")

    @property
    def stdSeverity(self) -> logging._Level:
        """
            Converts Coretex log severity into the
            equivalent log level from python std module logging

            Returns
            -------
            int -> python std module logging level

            Example
            -------
            >>> from coretex.logging import LogSeverity
            \b
            >>> print(LogSeverity.info.stdSeverity)
            20
        """

        if self == LogSeverity.fatal:
            return logging.FATAL

        if self == LogSeverity.error:
            return logging.ERROR

        if self == LogSeverity.warning:
            return logging.WARNING

        if self == LogSeverity.info:
            return logging.INFO

        if self == LogSeverity.debug:
            return logging.DEBUG

        raise RuntimeError(">> [Coretex] Invalid enum value")

    @property
    def prefix(self) -> str:
        """
            Prefix of the log severity

            Returns
            -------
            str -> prefix
        """

        return self.name.capitalize()

    @staticmethod
    def fromStd(logLevel: int) -> LogSeverity:
        """
            Converts python std module logging level
            into the equivalent log severity from coretex

            Returns
            -------
            LogSeverity -> Coretex log severity

            Example
            -------
            >>> import logging
            \b
            >>> from coretex.logging.log_severity import LogSeverity
            >>> logSeverityValue = LogSeverity.fromStd(logging.INFO)
            >>> print(logSeverityValue)
            LogSeverity.info
        """

        if logLevel == logging.FATAL:
            return LogSeverity.fatal

        if logLevel == logging.ERROR:
            return LogSeverity.error

        if logLevel == logging.WARNING:
            return LogSeverity.warning

        if logLevel == logging.INFO:
            return LogSeverity.info

        if logLevel == logging.DEBUG:
            return LogSeverity.debug

        raise ValueError(">> [Coretex] Invalid enum value")
