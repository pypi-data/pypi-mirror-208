from typing import Final

from .base_converter import ConverterProcessorType, BaseConverter
from .converters import *


class ConverterProcessorFactory:
    """
        Factory class used to create different types
        of BaseConverter objects based on the convertProcessorType
        property of the class

        Properties
        ----------
        convertProcessorType : ConverterProcessorType
            type of converter for convertin dataset
    """

    def __init__(self, convertProcessorType: ConverterProcessorType):
        self.type: Final = convertProcessorType

    def create(self, datasetName: str, spaceId: int, datasetPath: str) -> BaseConverter:
        """
            Creates BaseConverter based on the convertProcessorType
            property of the class

            Parameters
            ----------
            datasetName : str
                name of dataset
            spaceId : int
                id of Coretex Space
            datasetPath : str
                path to dataset

            Returns
            -------
            Appropriate BaseConverter object based on
            convertProcessorType
        """

        if self.type == ConverterProcessorType.coco:
            return COCOConverter(datasetName, spaceId, datasetPath)

        if self.type == ConverterProcessorType.yolo:
            return YoloConverter(datasetName, spaceId, datasetPath)

        if self.type ==  ConverterProcessorType.createML:
            return CreateMLConverter(datasetName, spaceId, datasetPath)

        if self.type == ConverterProcessorType.voc:
            return VOCConverter(datasetName, spaceId, datasetPath)

        if self.type == ConverterProcessorType.labelMe:
            return LabelMeConverter(datasetName, spaceId, datasetPath)

        if self.type == ConverterProcessorType.pascalSeg:
            return PascalSegConverter(datasetName, spaceId, datasetPath)

        if self.type == ConverterProcessorType.humanSegmentation:
            return HumanSegmentationConverter(datasetName, spaceId, datasetPath)

        if self.type == ConverterProcessorType.cityScape:
            return CityScapeConverter(datasetName, spaceId, datasetPath)

        raise RuntimeError()
