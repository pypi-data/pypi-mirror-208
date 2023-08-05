from typing import Optional
from typing_extensions import Self

from .custom_sample_data import CustomSampleData
from .local_custom_sample import LocalCustomSample
from ..network_sample import NetworkSample


class CustomSample(NetworkSample[CustomSampleData], LocalCustomSample):

    """
        Represents the custom Sample object from Coretex.ai\n
        Custom samples are used when working with Other Task\n
        Custom sample must be an archive
    """

    def __init__(self) -> None:
        NetworkSample.__init__(self)

    @classmethod
    def createCustomSample(
        cls,
        name: str,
        datasetId: int,
        filePath: str,
        mimeType: Optional[str] = None
    ) -> Optional[Self]:
        """
            Creates a new custom sample with specified properties\n
            For creating custom sample, sample must be an archive

            Parameters
            ----------
            name : str
                sample name
            datasetId : int
                id of dataset to which the sample will be added
            filePath : str
                path to the sample
            mimeType : Optional[str]
                mime type of the file, if None mime type guessing will be performed

            Returns
            -------
            Optional[Self] -> The created sample object or None if creation failed

            Example
            -------
            >>> from coretex import CustomSample
            \b
            >>> sample = CustomSample.createCustomSample("name", 1023, "path/to/file")
            >>> if sample is None:
                    print("Failed to create custom sample")
        """

        parameters = {
            "name": name,
            "dataset_id": datasetId
        }

        return cls._createSample(parameters, filePath, mimeType)
