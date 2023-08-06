from enum import IntEnum


class MetricType(IntEnum):

    """
        List of supported metric types
    """

    int = 1
    float = 2
    timestamp = 3
    interval = 4
    bytes = 5
    percent = 6
