from abc import ABC, abstractmethod
import hashlib
import io
from pathlib import Path

from PIL import Image

class ProcessorTemplate(ABC):
    extensions = ()

    def can_process_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.extensions

    def write_thumbnail(
        self,
        image: Image.Image,
        thumbnails_dir: Path,
        thumbnail_size: tuple[int, int],
    ) -> str:
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
        pass

    @abstractmethod
    def make_data_file(self, file_path: Path, data_files_dir: Path) -> str:
        pass

    def make_symlink_data_file(self, file_path: Path, data_files_dir: Path) -> str:
        extension = file_path.suffix
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        md5 = hashlib.md5(file_bytes).hexdigest()
        symlink_filename = f"{md5}{extension}"
        destination = data_files_dir / symlink_filename
        if not destination.exists():
            destination.symlink_to(file_path)
        return symlink_filename
