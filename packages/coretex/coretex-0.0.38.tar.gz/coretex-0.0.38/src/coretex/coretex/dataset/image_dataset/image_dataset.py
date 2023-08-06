from typing import TypeVar, Type, Optional, Dict, List

from .base import BaseImageDataset
from ..network_dataset import NetworkDataset
from ...sample import ImageSample
from ...annotation import ImageDatasetClass, ImageDatasetClasses
from ....codable import KeyDescriptor, Codable
from ....networking import networkManager, RequestType


DatasetType = TypeVar("DatasetType", bound = "ImageDataset")
SampleType = TypeVar("SampleType", bound = "ImageSample")


class ClassDistribution(Codable):

    name: str
    color: str
    count: int


class ImageDataset(BaseImageDataset[SampleType], NetworkDataset[SampleType]):  # type: ignore

    """
        Represents the Image Dataset class \n
        Includes functionality for working with Image Datasets
        that are uploaded to Coretex.ai
    """

    classDistribution: List[ClassDistribution]

    @classmethod
    def _keyDescriptors(cls) -> Dict[str, KeyDescriptor]:
        descriptors = super()._keyDescriptors()

        descriptors["samples"] = KeyDescriptor("sessions", ImageSample, list)
        descriptors["classes"] = KeyDescriptor("classes", ImageDatasetClass, ImageDatasetClasses)
        descriptors["classDistribution"] = KeyDescriptor("class_distribution", ClassDistribution, list)

        return descriptors

    @classmethod
    def fetchById(cls: Type[DatasetType], objectId: int, queryParameters: Optional[List[str]] = None) -> Optional[DatasetType]:
        obj = super().fetchById(objectId, queryParameters)
        if obj is None:
            return None

        response = networkManager.genericJSONRequest(
            endpoint=f"annotation-class?dataset_id={obj.id}",
            requestType=RequestType.get,
        )

        if not response.hasFailed():
            obj.classes = cls._decodeValue("classes", response.json)
            obj._writeClassesToFile()

        return obj

    def saveClasses(self, classes: ImageDatasetClasses) -> bool:
        parameters = {
            "dataset_id": self.id,
            "classes": [clazz.encode() for clazz in classes]
        }

        response = networkManager.genericJSONRequest("annotation-class", RequestType.post, parameters)
        if not response.hasFailed():
            return super().saveClasses(classes)

        return not response.hasFailed()
