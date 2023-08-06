from pathlib import Path

from ..image_dataset import LocalImageDataset
from ...sample import LocalObjectDetectionSample


class LocalObjectDetectionDataset(LocalImageDataset[LocalObjectDetectionSample]):

    """
        Represents the Local Object Detection Dataset class
        which is used for working locally with ObjectDetection Task type
    """

    def __init__(self, path: Path) -> None:
        super().__init__(path, LocalObjectDetectionSample)
