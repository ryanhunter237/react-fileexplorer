from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from PIL import Image
import pytest

from fileexplorer.proc import ProcessorTemplate

class MockProcessor(ProcessorTemplate):
    extensions = ('.jpg', '.png')

    def make_thumbnail(self, file_path: Path, thumbnails_dir: Path, thumbnail_size: tuple[int, int]) -> str | None:
        pass

    def make_data_file(self, file_path: Path, data_files_dir: Path) -> str:
        pass

@pytest.fixture
def mock_processor():
    return MockProcessor()

@pytest.fixture
def dummy_image():
    img = Image.new('RGB', (100, 100), color = 'red')
    return img

def test_can_process_file(mock_processor: ProcessorTemplate):
    assert mock_processor.can_process_file(Path("test.jpg"))
    assert mock_processor.can_process_file(Path("test.PNG"))
    assert not mock_processor.can_process_file(Path("test.txt"))

@patch("builtins.open", new_callable=mock_open)
def test_write_thumbnail(
    mock_file: MagicMock,
    mock_processor: MockProcessor,
    dummy_image: Image.Image,
    tmp_path: Path
):
    thumbnail_filename = mock_processor.write_thumbnail(dummy_image, tmp_path, (50, 50))
    assert thumbnail_filename.endswith('.png')
    mock_file.assert_called_with(tmp_path / thumbnail_filename, "wb")

@patch("builtins.open", new_callable=mock_open, read_data=b"dummy data")
@patch("pathlib.Path.symlink_to")
def test_make_symlink_data_file(
    mock_symlink: MagicMock,
    mock_open: MagicMock,
    mock_processor: MockProcessor,
    tmp_path: Path
):
    dummy_file_path = tmp_path / "test.jpg"
    data_files_dir = tmp_path / "data"
    data_files_dir.mkdir(exist_ok=True)
    symlink_filename = mock_processor.make_symlink_data_file(dummy_file_path, data_files_dir)
    assert symlink_filename.endswith('.jpg')
    mock_symlink.assert_called_with(dummy_file_path)
    mock_open.assert_called_with(dummy_file_path, "rb")
