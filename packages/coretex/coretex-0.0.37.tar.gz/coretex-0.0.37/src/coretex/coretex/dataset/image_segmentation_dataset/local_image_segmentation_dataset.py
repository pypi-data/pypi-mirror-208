from pathlib import Path

from ..image_dataset import LocalImageDataset
from ...sample import LocalImageSegmentationSample


class LocalImageSegmentationDataset(LocalImageDataset[LocalImageSegmentationSample]):

    """
        Represents the Local Image Segmentation Dataset class
        which is used for working locally with ImageSegmentation Task type
    """

    def __init__(self, path: Path) -> None:
        super().__init__(path, LocalImageSegmentationSample)
