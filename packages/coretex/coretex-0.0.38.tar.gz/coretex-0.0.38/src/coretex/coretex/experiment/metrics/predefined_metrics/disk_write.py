from typing import Optional

import psutil

from ..metric import Metric


class MetricDiskWrite(Metric):

    def __init__(self) -> None:
        diskIoCounters = psutil.disk_io_counters()

        if diskIoCounters is None:
            self.previousWrittenBytes = 0
        else:
            self.previousWrittenBytes = diskIoCounters.write_bytes

    def extract(self) -> Optional[float]:
        diskIoCounters = psutil.disk_io_counters()
        if diskIoCounters is None:
            return None

        currentWriteBytes = diskIoCounters.write_bytes
        writtenBytesDiff = currentWriteBytes - self.previousWrittenBytes

        self.previousWrittenBytes = currentWriteBytes

        return float(writtenBytesDiff)
