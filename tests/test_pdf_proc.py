from pathlib import Path
from unittest.mock import patch, MagicMock

from PIL import Image
import pytest

from fileexplorer.pdf_proc import PDFProcessor

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

mock_fitz_open = patch('fitz.open', return_value=MagicMock())
mock_pixmap = MagicMock()
mock_pixmap.width = 100
mock_pixmap.height = 100
mock_pixmap.samples = b'\x00\x00\x00' * 10000  # Example pixel data
mock_page = MagicMock(get_pixmap=MagicMock(return_value=mock_pixmap))
mock_pdf = MagicMock(load_page=MagicMock(return_value=mock_page))

@patch('PIL.Image.frombytes', return_value=MagicMock(spec=Image.Image))
@patch('fitz.open', return_value=mock_pdf)
def test_make_thumbnail_success(
    mocked_open: MagicMock,
    mock_image_frombytes: MagicMock,
    tmp_path: Path,
    pdf_processor: PDFProcessor
):
    thumbnail_path = tmp_path / "thumbnails"
    thumbnail_path.mkdir()
    file_path = tmp_path / "document.pdf"
    thumbnail_file = pdf_processor.make_thumbnail(file_path, thumbnail_path, (100, 100))
    assert thumbnail_file.endswith('.png')
    mocked_open.assert_called_once_with(file_path)
    mock_image_frombytes.assert_called_once_with(
        "RGB", [mock_pixmap.width, mock_pixmap.height], mock_pixmap.samples
    )

@patch('fileexplorer.proc.ProcessorTemplate.make_symlink_data_file')
def test_make_data_file(
    mock_symlink: MagicMock,
    tmp_path: Path,
    pdf_processor: PDFProcessor
):
    data_files_dir = tmp_path / "data"
    data_files_dir.mkdir()
    file_path = tmp_path / "document.pdf"
    pdf_processor.make_data_file(file_path, data_files_dir)
    mock_symlink.assert_called_once_with(
        file_path=file_path,
        data_files_dir=data_files_dir
    )
