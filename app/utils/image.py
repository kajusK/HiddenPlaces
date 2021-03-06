"""Image helpers."""
import os
from typing import Union
from PIL import Image
from werkzeug.datastructures import FileStorage


class Img:
    """Image manipulation helper."""

    def __init__(self, file: Union[str, FileStorage]):
        """Initializes the Img object
        Args:
            file: Path to file or uploaded file handle
        """
        self.image = Image.open(file)

    def thumbnail(self, dest: str, max_size: int) -> None:
        """Makes thumbnail from image.

        This alerts size of the internal loaded image too!

        Args:
            destination: Destination path to store result to
            max_size: Max size in either dimension of the image
        """
        self.image.thumbnail((max_size, max_size))
        self._mkdir(dest)
        params = {}
        if 'exif' in self.image.info:
            params['exif'] = self.image.info['exif']
        self.image.save(dest, **params)

    def _mkdir(self, path: str) -> None:
        """Creates target directory if doesn't exist yet.

        Args:
            path: Path to destination file
        """
        dest_dir = os.path.dirname(path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
