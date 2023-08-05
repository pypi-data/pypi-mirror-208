from pathlib import Path


class CustomSampleData:

    """
        Contains file and folder contents of the custom sample
    """

    def __init__(self, path: Path) -> None:
        self.folderContent = path.glob("*")
