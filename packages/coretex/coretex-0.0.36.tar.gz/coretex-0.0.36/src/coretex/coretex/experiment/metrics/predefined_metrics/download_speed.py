from ..metric import Metric
from ..utils import getNetworkUsage


class MetricDownloadSpeed(Metric):

    def extract(self) -> float:
        downloadSpeed, _ = getNetworkUsage()

        return downloadSpeed
