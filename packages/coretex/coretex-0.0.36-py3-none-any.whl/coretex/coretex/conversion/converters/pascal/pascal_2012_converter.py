from typing import List, Set

import os
import glob
import xml.etree.ElementTree as ET

from .shared import getTag, toFloat
from .instance_extractor import InstanceExtractor
from ...base_converter import BaseConverter
from .....coretex import CoretexImageAnnotation


class PascalSegConverter(BaseConverter):

    """
        Represents the Converter from Pascal VOC 2012 Format to Cortex Format
    """

    def __init__(self, datasetName: str, spaceId: int, datasetPath: str) -> None:
        super().__init__(datasetName, spaceId, datasetPath)

        self.__imagesPath = os.path.join(datasetPath, "JPEGImages")
        self.__segmentationPath = os.path.join(datasetPath, "SegmentationObject")

        annotations = os.path.join(datasetPath, "Annotations")
        self.__fileNames = glob.glob(os.path.join(annotations, "*.xml"))

    def _dataSource(self) -> List[str]:
        return self.__fileNames

    def _extractLabels(self) -> Set[str]:
        labels: Set[str] = set()

        for filename in self.__fileNames:
            tree = ET.parse(filename)
            root = tree.getroot()
            objects = root.findall("object")

            for obj in objects:
                labelElement = obj.find("name")
                if labelElement is None:
                    continue

                label = labelElement.text
                if label is None:
                    continue

                labels.add(label)

        return labels

    def __extractImageAnnotation(self, root: ET.Element) -> None:
        fileName = getTag(root, "filename")
        if fileName is None:
            return

        baseFileName = os.path.splitext(fileName)[0]
        filenamePNG = f"{baseFileName}.png"

        if not os.path.exists(os.path.join(self.__imagesPath, fileName)):
            return

        instanceExtractor = InstanceExtractor(self._dataset)
        instances = instanceExtractor.extractInstances(root, filenamePNG, self.__segmentationPath)

        size = root.find('size')
        if size is None:
            return

        width, height = toFloat(size, "width", "height")
        if width is None or height is None:
            return

        coretexAnnotation = CoretexImageAnnotation.create(fileName, width, height, instances)
        self._saveImageAnnotationPair(os.path.join(self.__imagesPath, fileName), coretexAnnotation)

    def _extractSingleAnnotation(self, fileName: str) -> None:
        tree = ET.parse(fileName)
        root = tree.getroot()

        self.__extractImageAnnotation(root)
