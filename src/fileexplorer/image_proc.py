from pathlib import Path

from PIL import Image

from fileexplorer.proc import ProcessorTemplate

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp',)

class ImageProcessor(ProcessorTemplate):
    """
    ImageProcessor is a subclass of ProcessorTemplate specifically designed for
    processing image files. It overrides methods to create thumbnails and
    symbolic links as data files for supported image formats.

    Attributes:
    extensions (tuple[str, ...]): A tuple containing the file extensions that 
                                  this processor can handle.
    """
    extensions = IMAGE_EXTENSIONS

    def make_thumbnail(
        self,
        file_path: Path,
        thumbnails_dir: Path,
        thumbnail_size: tuple[int, int]
    ) -> str | None:
        """
        Generate a thumbnail for an image file.

        This method attempts to open an image file, and if successful, it calls
        the write_thumbnail method to create and save the thumbnail.

        Parameters:
        file_path (Path): The path of the image file.
        thumbnails_dir (Path): The directory to save the thumbnail.
        thumbnail_size (tuple[int, int]): The desired dimensions (width, height) 
                                         of the thumbnail.

        Returns:
        str | None: The filename of the generated thumbnail if successful, 
                    otherwise None.
        """
        try:
            image = Image.open(file_path)
        except Exception:
            return None
        thumbnail_filename = self.write_thumbnail(
            image=image,
            thumbnails_dir=thumbnails_dir,
            thumbnail_size=thumbnail_size
        )
        return thumbnail_filename

    def make_data_file(self, file_path: Path, data_files_dir: Path) -> str:
        """
        Create a symbolic link for the given image file in the specified directory.

        This method delegates the creation of a symbolic link for the image file
        to the make_symlink_data_file method of the ProcessorTemplate.

        Parameters:
        file_path (Path): The path of the image file.
        data_files_dir (Path): The directory to create the symbolic link in.

        Returns:
        str: The filename of the created symbolic link.
        """
        return self.make_symlink_data_file(
            file_path=file_path,
            data_files_dir=data_files_dir
        )