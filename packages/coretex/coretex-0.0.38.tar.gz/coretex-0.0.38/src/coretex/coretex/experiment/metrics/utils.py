from typing import Tuple

import time

import psutil


def getNetworkUsage() -> Tuple[float, float]:
    netIOCounters1 = psutil.net_io_counters(pernic=True)
    time.sleep(1)
    netIOCounters2 = psutil.net_io_counters(pernic=True)

    totalBytesRecv = 0
    totalBytesSent = 0

    for interface, counters1 in netIOCounters1.items():
        counters2 = netIOCounters2[interface]

        bytesRecv = counters2.bytes_recv - counters1.bytes_recv
        bytesSent = counters2.bytes_sent - counters1.bytes_sent

        totalBytesRecv += bytesRecv
        totalBytesSent += bytesSent

    return float(totalBytesRecv * 8), float(totalBytesSent * 8)
