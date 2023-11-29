from abc import ABC, abstractmethod
import hashlib
import io
from pathlib import Path

from PIL import Image

class ProcessorTemplate(ABC):
    extensions = ()

    def can_process_file(self, file_path: Path) -> bool:
        """
        Determine if the processor can handle the given file based on its extension.

        Parameters:
        file_path (Path): The path of the file to check.

        Returns:
        bool: True if the file can be processed by this processor, False otherwise.
        """
        return file_path.suffix.lower() in self.extensions

    def write_thumbnail(
        self,
        image: Image.Image,
        thumbnails_dir: Path,
        thumbnail_size: tuple[int, int],
    ) -> str:
        """
        Generate and save a thumbnail for the provided image.

        Parameters:
        image (Image.Image): The image object to create a thumbnail from.
        thumbnails_dir (Path): The directory where the thumbnail should be saved.
        thumbnail_size (tuple[int, int]): The size of the thumbnail (width, height).

        Returns:
        str: The filename of the saved thumbnail.
        """
        image.thumbnail(thumbnail_size)
        image_bytes_io = io.BytesIO()
        image.save(image_bytes_io, format="png")
        image_bytes = image_bytes_io.getvalue()
        md5 = hashlib.md5(image_bytes).hexdigest()
        thumbnail_filename = f"{md5}.png"
        with open(thumbnails_dir / thumbnail_filename, "wb") as f:
            f.write(image_bytes)
        return thumbnail_filename

    @abstractmethod
    def make_thumbnail(
        self,
        file_path: Path,
        thumbnails_dir: Path,
        thumbnail_size: tuple[int, int]
    ) -> str | None:
        """
        Abstract method to generate a thumbnail from a given file.

        This method should be implemented in subclasses to handle specific file types.

        Parameters:
        file_path (Path): The path of the file to create a thumbnail from.
        thumbnails_dir (Path): The directory to save the thumbnail.
        thumbnail_size (tuple[int, int]): Desired dimensions for the thumbnail.

        Returns:
        str | None: The filename of the thumbnail if created, otherwise None.
        """
        pass

    @abstractmethod
    def make_data_file(self, file_path: Path, data_files_dir: Path) -> str:
        """
        Abstract method to create a data file from the given file.

        This method should be implemented in subclasses to handle specific file types.

        Parameters:
        file_path (Path): The path of the file to create a data file from.
        data_files_dir (Path): The directory to save the data file.

        Returns:
        str: The filename of the created data file.
        """
        pass

    def make_symlink_data_file(self, file_path: Path, data_files_dir: Path) -> str:
        """
        Create a symbolic link for the given file in the specified directory.

        Parameters:
        file_path (Path): The path of the file to create a symbolic link for.
        data_files_dir (Path): The directory where the symbolic link will be created.

        Returns:
        str: The filename of the symbolic link.
        """
        extension = file_path.suffix
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        md5 = hashlib.md5(file_bytes).hexdigest()
        symlink_filename = f"{md5}{extension}"
        destination = data_files_dir / symlink_filename
        if not destination.exists():
            destination.symlink_to(file_path)
        return symlink_filename
