from typing import Optional, Union
from typing_extensions import Self
from pathlib import Path

from ..image_sample import ImageSample


class ImageSegmentationSample(ImageSample):

    """
        Represents sample linked to task of type Image Segmentation from Coretex.ai
    """

    @classmethod
    def createImageSegmentationSample(cls, datasetId: int, imagePath: Union[Path, str]) -> Optional[Self]:
        """
            Creates a new sample from the provided path and adds sample to specified dataset

            Parameters
            ----------
            datasetId : int
                id of dataset to which sample will be added
            imagePath : Union[Path, str]
                path to the sample

            Returns
            -------
            Optional[Self] -> The created sample object or None if creation failed

            Example
            -------
            >>> from coretex import ImageSegmentationSample
            \b
            >>> sample = ImageSegmentationSample.createImageSegmentationSample(1023, "path/to/file.jpeg")
            >>> if sample is None:
                    print("Failed to create image segmentation sample")
        """

        return cls.createImageSample(datasetId, imagePath)
