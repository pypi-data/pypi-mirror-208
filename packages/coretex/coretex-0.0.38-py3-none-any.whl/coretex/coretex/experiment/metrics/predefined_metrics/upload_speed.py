from ..metric import Metric
from ..utils import getNetworkUsage


class MetricUploadSpeed(Metric):

    def extract(self) -> float:
        _, uploadSpeed = getNetworkUsage()

        return uploadSpeed
