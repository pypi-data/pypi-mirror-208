from typing import Type, Optional

from .metric import Metric
from .predefined_metrics import *


def getClassForMetric(name: str) -> Optional[Type[Metric]]:
    if name == "disk_read":
        return MetricDiskRead

    if name == "disk_write":
        return MetricDiskWrite

    if name == "cpu_usage":
        return MetricCPUUsage

    if name == "ram_usage":
        return MetricRAMUsage

    if name == "gpu_usage":
        return MetricGPUUsage

    if name == "gpu_temperature":
        return MetricGPUTemperature

    if name == "upload_speed":
        return MetricUploadSpeed

    if name == "download_speed":
        return MetricDownloadSpeed

    return None
