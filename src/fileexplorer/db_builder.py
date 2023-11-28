import hashlib
import io
import multiprocessing
from pathlib import Path

import fitz
from flask import Flask
from PIL import Image

from fileexplorer import models
from fileexplorer.models import (
    create_tables,
    insert_thumbnail,
    thumbnail_exists_for_file,
    insert_data_file,
)

THUMBNAIL_SIZE = (100, 100)


def build_database_async(app: Flask):
    database_path = app.config["DATABASE_PATH"]
    root_dir = Path(app.config["ROOT_DIR"])
    resources_dir = Path(app.config["RESOURCES_DIR"])
    supported_extension = app.config["SUPPORTED_EXTENSIONS"]
    worker = multiprocessing.Process(
        target=build_database,
        args=(database_path, root_dir, resources_dir, supported_extension),
    )
    worker.start()


def build_database(
    database_path: str,
    root_dir: Path,
    resources_dir: Path,
    supported_extensions: list[str],
):
    models.DATABASE_PATH = database_path
    create_tables()
    make_resources_directories(resources_dir)
    thumbnails_dir = resources_dir / "thumbnails"
    files_dir = resources_dir / "files"
    for file_path in Path(root_dir).rglob("*"):
        if not file_path.is_file():
            continue
        if thumbnail_exists_for_file(file_path):
            continue
        extension = file_path.suffix.lower()
        if extension not in supported_extensions:
            continue
        elif extension in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
            thumbnail_filename = get_image_thumbnail(file_path, thumbnails_dir)
            data_filename = get_symlink_filename(file_path, files_dir)
        elif extension == ".pdf":
            thumbnail_filename = get_pdf_thumbnail(file_path, thumbnails_dir)
            data_filename = get_symlink_filename(file_path, files_dir)
        # elif extension == '.stl':
        #     thumbnail_filename = get_stl_thumbnail(file_path, resources_dir)
        else:
            thumbnail_filename = None
        insert_thumbnail(file_path, thumbnail_filename)
        insert_data_file(file_path, data_filename)


def make_resources_directories(resources_dir: Path):
    resources_dir.mkdir(parents=True, exist_ok=True)
    thumbnails_dir = resources_dir / "thumbnails"
    thumbnails_dir.mkdir(exist_ok=True)
    files_dir = resources_dir / "files"
    files_dir.mkdir(exist_ok=True)


def write_thumbnail(image: Image.Image, thumbnails_dir: Path) -> str:
    image.thumbnail(THUMBNAIL_SIZE)
    image_bytes_io = io.BytesIO()
    image.save(image_bytes_io, format="png")
    image_bytes = image_bytes_io.getvalue()
    md5 = hashlib.md5(image_bytes).hexdigest()
    thumbnail_filename = f"{md5}.png"
    with open(thumbnails_dir / thumbnail_filename, "wb") as f:
        f.write(image_bytes)
    return thumbnail_filename


def get_image_thumbnail(file: Path, thumbnails_dir: Path) -> str | None:
    try:
        image = Image.open(file)
    except Exception:
        return None
    thumbnail_filename = write_thumbnail(image, thumbnails_dir)
    return thumbnail_filename


def get_pdf_thumbnail(file: Path, resources_dir: Path) -> str | None:
    try:
        pdf = fitz.open(file)
        first_page = pdf.load_page(0)
        pix = first_page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    except Exception:
        return None
    thumbnail_filename = write_thumbnail(image, resources_dir)
    return thumbnail_filename


def get_symlink_filename(file: Path, files_dir: Path) -> str:
    extension = file.suffix
    with open(file, "rb") as f:
        file_bytes = f.read()
    md5 = hashlib.md5(file_bytes).hexdigest()
    symlink_filename = f"{md5}{extension}"
    destination = files_dir / symlink_filename
    if not destination.exists():
        destination.symlink_to(file)
    return symlink_filename
