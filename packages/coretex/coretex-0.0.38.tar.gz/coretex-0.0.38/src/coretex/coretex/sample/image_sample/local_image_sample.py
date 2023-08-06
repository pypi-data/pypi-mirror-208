from pathlib import Path
from zipfile import ZipFile

import json
import os

from .image_sample_data import AnnotatedImageSampleData
from ..local_sample import LocalSample
from ...annotation import CoretexImageAnnotation


class LocalImageSample(LocalSample[AnnotatedImageSampleData]):

    """
        Represents the local Image Sample object\n
        Contains basic properties and functionality for local image Sample classes\n
        The class has several methods that allow users to access and
        manipulate local image data and annotations
    """

    def load(self) -> AnnotatedImageSampleData:
        """
            Loads image and its annotation if it exists

            Returns
            -------
            AnnotatedImageSampleData -> image data and annotation in Coretex.ai format
        """

        return AnnotatedImageSampleData(Path(self.path))

    def saveAnnotation(self, coretexAnnotation: CoretexImageAnnotation) -> bool:
        """
            Updates annotation for the image

            Returns
            -------
            bool -> returns True if successful, False otherwise
        """

        with open(Path(self.path) / "annotations.json", "w") as file:
            json.dump(coretexAnnotation.encode(), file)

        zipPath = Path(self.zipPath)

        oldZipPath = zipPath.parent / f"{zipPath.stem}-old.zip"
        zipPath.rename(oldZipPath)

        with ZipFile(zipPath, "w") as zipFile:
            path = Path(self.path)
            for element in os.listdir(path):
                zipFile.write(path / element, arcname = element)

        oldZipPath.unlink()
        return True
