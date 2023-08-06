from typing import Optional, TypeVar, Generic, List, Callable
from abc import ABC, abstractmethod
from pathlib import Path

from ..sample import Sample


SampleType = TypeVar("SampleType", bound = "Sample")


class Dataset(ABC, Generic[SampleType]):

    """
        Represents the generic class Dataset
        Includes methods that can be used by any instance of Dataset
        and abstract methods that must be implemented by any subclass

        Properties
        ----------
        name : str
            name of dataset
        samples : List[SampleType]
            list of samples
    """

    name: str
    samples: List[SampleType]

    @property
    def count(self) -> int:
        """
            Returns
            -------
            int -> number of samples in this dataset
        """

        return len(self.samples)

    @property
    @abstractmethod
    def path(self) -> Path:
        pass

    @abstractmethod
    def download(self, ignoreCache: bool = False) -> None:
        pass

    def add(self, sample: SampleType) -> bool:
        """
            Adds the specified sample into the dataset

            Parameters
            ----------
            sample : SampleType
                sample which should be added into the dataset

            Returns
            -------
            bool -> True if sample was added, False if sample was not added
        """

        self.samples.append(sample)
        return True

    def rename(self, name: str) -> bool:
        """
            Renames the dataset, if the provided name is
            different from the current name

            Parameters
            ----------
            name : str
                new dataset name

            Returns
            -------
            bool -> True if dataset was renamed, False if dataset was not renamed
        """

        if self.name == name:
            return False

        self.name = name
        return True

    def getSample(self, name: str) -> Optional[SampleType]:
        """
            Retrieves sample which matches the provided name

            Parameters
            ----------
            name : str
                name of sample

            Returns
            -------
            Optional[SampleType] -> sample object
        """

        for sample in self.samples:
            # startswith must be used since if we import sample
            # with the same name twice, the second one will have
            # suffix with it's serial number
            if sample.name.startswith(name):
                return sample

        return None

    def getSamples(self, filterFunc: Callable[[SampleType], bool]) -> List[SampleType]:
        filteredSamples: List[SampleType] = []

        for sample in self.samples:
            if filterFunc(sample):
                filteredSamples.append(sample)

        return filteredSamples
