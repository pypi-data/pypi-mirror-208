from pathlib import Path

from .custom_sample_data import CustomSampleData
from ..local_sample import LocalSample


class LocalCustomSample(LocalSample[CustomSampleData]):

    """
        Represents the local custom Sample class
        which is used for working with Other Task locally
    """

    def load(self) -> CustomSampleData:
        """
            Returns
            -------
            CustomSampleData -> file and folder contents of the custom sample
        """
        return CustomSampleData(Path(self.path))
