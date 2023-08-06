from typing import Dict

from .base import BaseCustomDataset
from ..network_dataset import NetworkDataset
from ...sample import CustomSample
from ....codable import KeyDescriptor


class CustomDataset(BaseCustomDataset, NetworkDataset[CustomSample]):

    """
        Custom Dataset class which is used for Other Task
        Represents the collection of archived samples
    """

    @classmethod
    def _keyDescriptors(cls) -> Dict[str, KeyDescriptor]:
        descriptors = super()._keyDescriptors()
        descriptors["samples"] = KeyDescriptor("sessions", CustomSample, list)

        return descriptors
