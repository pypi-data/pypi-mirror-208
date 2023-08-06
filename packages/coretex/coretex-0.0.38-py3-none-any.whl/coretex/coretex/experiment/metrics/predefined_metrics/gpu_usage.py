from py3nvml import py3nvml

from ..metric import Metric


class MetricGPUUsage(Metric):

    def extract(self) -> float:
        handle = py3nvml.nvmlDeviceGetHandleByIndex(0)
        utilization = py3nvml.nvmlDeviceGetUtilizationRates(handle)
        gpuUsage = utilization.gpu

        return float(gpuUsage)
