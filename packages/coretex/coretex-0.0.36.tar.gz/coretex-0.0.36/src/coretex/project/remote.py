from tap import Tap
from typing import Tuple

from .base import ProjectCallback
from ..networking import NetworkManager


class RemoteArgumentParser(Tap):

    refreshToken: str
    experimentId: int

    def configure(self) -> None:
        self.add_argument("--refreshToken", type = str)
        self.add_argument("--experimentId", type = int)


def processRemote() -> Tuple[int, ProjectCallback]:
    remoteArgumentParser = RemoteArgumentParser().parse_args()

    response = NetworkManager.instance().authenticateWithRefreshToken(remoteArgumentParser.refreshToken)
    if response.hasFailed():
        raise RuntimeError(">> [Coretex] Failed to authenticate")

    return remoteArgumentParser.experimentId, ProjectCallback.create(remoteArgumentParser.experimentId, remoteArgumentParser.refreshToken)
