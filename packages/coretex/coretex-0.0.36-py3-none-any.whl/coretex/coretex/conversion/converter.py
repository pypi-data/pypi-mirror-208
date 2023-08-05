from typing import Optional

from .converter_processor_factory import ConverterProcessorFactory
from .base_converter import ConverterProcessorType
from ..dataset import ImageDataset


def convert(type: ConverterProcessorType, datasetName: str, spaceId: int, datasetPath: str) -> Optional[ImageDataset]:
    """
        Converts and uploads the given dataset to Coretex Format

        Parameters
        ----------
        type : ConverterProcessorType
            dataset format type (coco, yolo, createML, voc, labelMe, pascalSeg)
        datasetName : str
            name of dataset
        spaceId : str
            id of Coretex Space
        datasetPath : str
            path to dataset

        Returns
        -------
        Optional[ImageDataset] -> The converted ImageDataset object

        Example
        -------
        >>> from coretex import convert, ConverterProcessorType
        \b
        >>> dataset = convert(
                type = ConvertProcessorType.coco,
                datasetName = "coretex_dataset",
                spaceId = 1023,
                datasetPath = "path/to/dataset"
            )
        >>> if dataset is not None:
                print("Dataset converted successfully")
    """

    return ConverterProcessorFactory(type).create(datasetName, spaceId, datasetPath).convert()
