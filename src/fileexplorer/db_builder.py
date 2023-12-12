import multiprocessing
from pathlib import Path

from flask import Flask

from fileexplorer import models
from fileexplorer.models import (
    create_tables,
    insert_thumbnail,
    insert_data_file,
)
from fileexplorer.image_proc import ImageProcessor
from fileexplorer.pdf_proc import PdfProcessor
from fileexplorer.stl_proc import StlProcessor

THUMBNAIL_SIZE = (100, 100)

def build_database_async(app: Flask, testing: bool=False):
    database_path = app.config["DATABASE_PATH"]
    root_dir = Path(app.config["ROOT_DIR"])
    resources_dir = Path(app.config["RESOURCES_DIR"])
    supported_extensions = app.config["SUPPORTED_EXTENSIONS"]
    build_args = (database_path, root_dir, resources_dir, supported_extensions)
    if testing:
        done_flag = multiprocessing.Event()
        build_args += (done_flag,)
    worker = multiprocessing.Process(
        target=build_database,
        args=build_args,
    )
    worker.start()
    if testing:
        done_flag.wait()

def build_database(
    database_path: str,
    root_dir: Path,
    resources_dir: Path,
    supported_extensions: list[str],
    done_flag: multiprocessing.Event=None
):
    models.DATABASE_PATH = database_path
    create_tables()
    make_resources_directories(resources_dir)
    processors = [ImageProcessor(), PdfProcessor(), StlProcessor()]
    for file_path in Path(root_dir).rglob("*"):
        if not file_path.is_file():
            continue
        # if thumbnail_exists_for_file(file_path):
        #     continue
        if file_path.suffix.lower() not in supported_extensions:
            continue
        thumbnail_filename = None
        data_filename = None
        for processor in processors:
            if not processor.can_process_file(file_path):
                continue
            thumbnail_filename = processor.make_thumbnail(
                file_path=file_path,
                thumbnails_dir=resources_dir / "thumbnails",
                thumbnail_size=THUMBNAIL_SIZE
            )
            if thumbnail_filename is None:
                continue
            data_filename = processor.make_data_file(
                file_path=file_path,
                data_files_dir=resources_dir / "files"
            )
        if (thumbnail_filename is not None) and (data_filename is not None):
            insert_thumbnail(file_path, thumbnail_filename)
            insert_data_file(file_path, data_filename)
    if done_flag:
        done_flag.set()

def make_resources_directories(resources_dir: Path):
    resources_dir.mkdir(parents=True, exist_ok=True)
    thumbnails_dir = resources_dir / "thumbnails"
    thumbnails_dir.mkdir(exist_ok=True)
    files_dir = resources_dir / "files"
    files_dir.mkdir(exist_ok=True)