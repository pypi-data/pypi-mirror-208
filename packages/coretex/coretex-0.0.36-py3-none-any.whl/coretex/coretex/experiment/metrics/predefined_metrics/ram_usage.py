import psutil

from ..metric import Metric


class MetricRAMUsage(Metric):

    def extract(self) -> float:
        return float(psutil.virtual_memory().percent)
