import logging

from .dataset import Dataset


def downloadDataset(dataset: Dataset) -> None:
    # TODO: Should we think about using deprecation package for handling this?
    logging.getLogger("coretexpylib").warning(">> [Coretex] (downloadDataset) function is deprecated use Dataset.download instead")

    dataset.download()
