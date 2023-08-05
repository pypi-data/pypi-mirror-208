from typing import Optional

import psutil

from ..metric import Metric


class MetricDiskRead(Metric):

    def __init__(self) -> None:
        diskIoCounters = psutil.disk_io_counters()

        if diskIoCounters is None:
            self.previousReadBytes = 0
        else:
            self.previousReadBytes = diskIoCounters.read_bytes

    def extract(self) -> Optional[float]:
        diskIoCounters = psutil.disk_io_counters()
        if diskIoCounters is None:
            return None

        currentReadBytes = diskIoCounters.read_bytes
        readBytesDiff = currentReadBytes - self.previousReadBytes

        self.previousReadBytes = currentReadBytes

        return float(readBytesDiff)
