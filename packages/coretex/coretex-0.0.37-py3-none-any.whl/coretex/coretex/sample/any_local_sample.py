from typing import TypeVar

from .local_sample import LocalSample


SampleDataType = TypeVar("SampleDataType")


class AnyLocalSample(LocalSample[SampleDataType]):

    """
        Generic class for local samples
    """

    @property
    def path(self) -> str:
        """
            Returns
            -------
            str -> path for any local sample
        """

        return str(self._path)

    @property
    def zipPath(self) -> str:
        """
            Returns
            -------
            str -> zip path for any local sample
        """

        return str(self._path)
