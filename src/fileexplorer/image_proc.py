from pathlib import Path

from PIL import Image

from fileexplorer.proc import ProcessorTemplate

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp',)

class ImageProcessor(ProcessorTemplate):
    extensions = IMAGE_EXTENSIONS

    def make_thumbnail(
        self,
        file_path: Path,
        thumbnails_dir: Path,
        thumbnail_size: tuple[int, int]
    ) -> str | None:
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
        return self.make_symlink_data_file(
            file_path=file_path,
            data_files_dir=data_files_dir
        )