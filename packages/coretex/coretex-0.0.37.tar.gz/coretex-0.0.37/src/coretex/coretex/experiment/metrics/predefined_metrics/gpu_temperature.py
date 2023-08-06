from py3nvml import py3nvml

from ..metric import Metric


class MetricGPUTemperature(Metric):

    def extract(self) -> float:
        handle = py3nvml.nvmlDeviceGetHandleByIndex(0)
        temperature = py3nvml.nvmlDeviceGetTemperature(handle, py3nvml.NVML_TEMPERATURE_GPU)

        return float(temperature)
