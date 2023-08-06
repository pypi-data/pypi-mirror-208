import psutil

from ..metric import Metric


class MetricCPUUsage(Metric):

    def extract(self) -> float:
        return float(psutil.cpu_percent(5))
