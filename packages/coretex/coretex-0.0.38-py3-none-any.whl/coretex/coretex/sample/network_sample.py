from typing import Any, TypeVar, Optional, Generic, Dict, Union
from typing_extensions import Self
from pathlib import Path

import os

from .sample import Sample
from ..space import SpaceTask
from ...codable import KeyDescriptor
from ...networking import NetworkObject, networkManager
from ...folder_management import FolderManager
from ...utils import guessMimeType


SampleDataType = TypeVar("SampleDataType")


class NetworkSample(Generic[SampleDataType], Sample[SampleDataType], NetworkObject):

    """
        Represents a base class for all Sample classes which are
        comunicating with Coretex.ai
    """

    isLocked: bool
    spaceTask: SpaceTask

    @property
    def path(self) -> str:
        """
            Returns
            -------
            str -> path for network sample
        """

        return os.path.join(FolderManager.instance().samplesFolder, str(self.id))

    @property
    def zipPath(self) -> str:
        """
            Returns
            -------
            str -> zip path for network sample
        """

        return f"{self.path}.zip"

    @classmethod
    def _keyDescriptors(cls) -> Dict[str, KeyDescriptor]:
        descriptors = super()._keyDescriptors()
        descriptors["spaceTask"] = KeyDescriptor("project_task", SpaceTask)

        return descriptors

    @classmethod
    def _endpoint(cls) -> str:
        return "session"

    @classmethod
    def _createSample(
        cls,
        parameters: Dict[str, Any],
        filePath: Union[Path, str],
        mimeType: Optional[str] = None
    ) -> Optional[Self]:
        """
            Uploads sample to Coretex.ai

            Parametrs
            ---------
            endpoint : str
                API endpoint
            parameters : Dict[str, Any]
                parameters which will be sent as request body
            filePath : str
                path to sample
            mimeType : Optional[str]
                mimeType (not required)

            Returns
            -------
            Optional[Self] -> created sample object if request
            was successful, None otherwise
        """

        if isinstance(filePath, str):
            filePath = Path(filePath)

        if mimeType is None:
            mimeType = guessMimeType(str(filePath))

        with filePath.open("rb") as sampleFile:
            files = [
                ("file", (filePath.stem, sampleFile, mimeType))
            ]

            response = networkManager.genericUpload("session/import", files, parameters)
            if response.hasFailed():
                return None

            return cls.decode(response.json)

    def download(self, ignoreCache: bool = False) -> bool:
        """
            Downloads sample from Coretex.ai

            Returns
            -------
            bool -> False if response is failed, True otherwise
        """

        if os.path.exists(self.zipPath) and not ignoreCache:
            return True

        response = networkManager.genericDownload(
            endpoint = f"{self.__class__._endpoint()}/export?id={self.id}",
            destination = self.zipPath
        )

        return not response.hasFailed()

    def load(self) -> SampleDataType:
        return super().load()  # type: ignore
