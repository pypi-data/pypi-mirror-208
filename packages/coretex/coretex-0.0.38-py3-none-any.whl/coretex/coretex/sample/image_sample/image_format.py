from enum import IntEnum


class ImageFormat(IntEnum):

    """
        List of available image formats on Coretex.ai
    """

    jpg = 0
    png = 1

    @property
    def extension(self) -> str:
        if self == ImageFormat.jpg:
            return "jpeg"

        return self.name
