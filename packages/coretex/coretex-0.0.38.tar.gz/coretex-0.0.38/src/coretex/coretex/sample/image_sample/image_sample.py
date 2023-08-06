from typing import Optional, Union
from typing_extensions import Self
from pathlib import Path

from .image_sample_data import AnnotatedImageSampleData
from .local_image_sample import LocalImageSample
from .image_format import ImageFormat
from ..network_sample import NetworkSample
from ...annotation import CoretexImageAnnotation
from ....networking import networkManager, RequestType


class ImageSample(NetworkSample[AnnotatedImageSampleData], LocalImageSample):

    """
        Represents the generic image sample\n
        Contains basic properties and functionality for all image sample classes\n
        The class has several methods that allow users to access and
        manipulate image data and annotations, as well as to create new image samples
    """

    def __init__(self) -> None:
        NetworkSample.__init__(self)

    @property
    def imagePath(self) -> Path:
        path = Path(self.path)

        for format in ImageFormat:
            imagePaths = list(path.glob(f"*.{format.extension}"))
            imagePaths = [path for path in imagePaths if not "thumbnail" in str(path)]

            if len(imagePaths) > 0:
                return Path(imagePaths[0])

        raise FileNotFoundError

    @property
    def annotationPath(self) -> Path:
        return Path(self.path) / "annotations.json"

    def saveAnnotation(self, coretexAnnotation: CoretexImageAnnotation) -> bool:
        super().saveAnnotation(coretexAnnotation)

        parameters = {
            "id": self.id,
            "data": coretexAnnotation.encode()
        }

        response = networkManager.genericJSONRequest(
            endpoint = "session/save-annotations",
            requestType = RequestType.post,
            parameters = parameters
        )

        return not response.hasFailed()

    @classmethod
    def createImageSample(cls, datasetId: int, imagePath: Union[Path, str]) -> Optional[Self]:
        """
            Creates a new image sample with specified properties\n
            For creating custom sample, sample must be an image of supported format

            Parameters
            ----------
            datasetId : int
                id of dataset in which image sample will be created
            imagePath : Union[Path, str]
                path to the image sample

            Returns
            -------
            The created image sample object

            Example
            -------
            >>> from coretex import ImageSample
            \b
            >>> sample = ImageSample.createImageSample(1023, "path/to/file.jpeg")
            >>> if sample is None:
                    print("Failed to create image sample")
        """

        parameters = {
            "dataset_id": datasetId
        }

        return cls._createSample(parameters, imagePath)
