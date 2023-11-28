from pathlib import Path

import fitz
from PIL import Image

from fileexplorer.proc import ProcessorTemplate

PDF_EXTENSIONS = ('.pdf',)

class PDFProcessor(ProcessorTemplate):
    def __init__(self):
        self.extensions = PDF_EXTENSIONS

    def make_thumbnail(
        self,
        file_path: Path,
        thumbnails_dir: Path,
        thumbnail_size: tuple[int, int]
    ) -> str | None:
        try:
            pdf = fitz.open(file_path)
            first_page = pdf.load_page(0)
            pix = first_page.get_pixmap()
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        except Exception as e:
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