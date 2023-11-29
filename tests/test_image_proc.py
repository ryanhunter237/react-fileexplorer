import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock

from PIL import Image
import pytest

from fileexplorer.image_proc import ImageProcessor

@pytest.fixture
def image_processor():
    return ImageProcessor()

@patch('PIL.Image.open', return_value=MagicMock(spec=Image.Image))
def test_make_thumbnail_success(
    mocked_open: MagicMock,
    tmp_path: Path,
    image_processor: ImageProcessor
):
    thumbnail_path = tmp_path / "thumbnails"
    thumbnail_path.mkdir()
    file_path = tmp_path / "image.jpg"
    thumbnail_filename = image_processor.make_thumbnail(
        file_path, thumbnail_path, (100, 100)
    )
    empty_md5 = hashlib.md5(b'').hexdigest()
    assert thumbnail_filename == f'{empty_md5}.png'
    mocked_open.assert_called_once_with(file_path)

@patch('PIL.Image.open', side_effect=Exception)
def test_make_thumbnail_fail(
    mocked_open: MagicMock,
    tmp_path: Path,
    image_processor: ImageProcessor
):
    thumbnail_path = tmp_path / "thumbnails"
    thumbnail_path.mkdir()
    file_path = tmp_path / "image.jpg"
    thumbnail_filename = image_processor.make_thumbnail(
        file_path, thumbnail_path, (100, 100)
    )
    assert thumbnail_filename is None
    mocked_open.assert_called_once_with(file_path)

@patch('fileexplorer.proc.ProcessorTemplate.make_symlink_data_file')
def test_make_data_file(
    mock_symlink: MagicMock,
    tmp_path: Path,
    image_processor: ImageProcessor
):
    data_files_dir = tmp_path / "data"
    data_files_dir.mkdir()
    file_path = tmp_path / "image.jpg"
    file_path.touch()
    image_processor.make_data_file(file_path, data_files_dir)
    mock_symlink.assert_called_once_with(file_path=file_path, data_files_dir=data_files_dir)
