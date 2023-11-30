import hashlib
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask
from flask.testing import FlaskClient 
from PIL import Image
import pytest
from pytest import TempPathFactory

from fileexplorer import create_app

# Helper functions for pytest tests
def create_test_app(root_dir: Path, instance_dir: Path) -> Flask:
    resources_dir = instance_dir / 'resources'
    database_path = instance_dir / 'files.db'
    test_config = {
        "TESTING": True,
        "ROOT_DIR": root_dir.as_posix(),
        "RESOURCES_DIR": resources_dir.as_posix(),
        "DATABASE_PATH": database_path.as_posix()
    }
    return create_app(test_config)

def get_file_md5(file_path: Path) -> str:
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    return hashlib.md5(file_bytes).hexdigest()

# root_dir and test_client fixtures to test the /api/directory-parts/  
# Directory structure is
# root_dir/subdir1/subdir2/file.txt
@pytest.fixture(scope="session")
def nested_directories_root_dir(tmp_path_factory: TempPathFactory) -> Path:
    root_dir = tmp_path_factory.mktemp('root-dir')
    (root_dir / 'subdir1/subdir2').mkdir(parents=True)
    (root_dir / 'file.txt').touch()
    return root_dir

@pytest.fixture(scope="session")
def nested_directories_client(
    nested_directories_root_dir: Path,
    tmp_path_factory: TempPathFactory
) -> FlaskClient:
    instance_dir = tmp_path_factory.mktemp('instance-dir')
    app = create_test_app(nested_directories_root_dir, instance_dir)
    return app.test_client()

def test_directory_parts_root_dir(
    nested_directories_root_dir: Path,
    nested_directories_client: FlaskClient
):
    response = nested_directories_client.get('/api/directory-parts/')
    assert response.status_code == 200
    parts = response.json
    assert parts[0]['part'] == nested_directories_root_dir.as_posix()
    assert urlparse(parts[0]['directory-info-url']).path == '/api/directory-info/'

def test_directory_parts_redirect(nested_directories_client: FlaskClient):
    response = nested_directories_client.get('/api/directory-parts')
    assert response.status_code == 308
    redirect_location = response.headers['Location']
    assert urlparse(redirect_location).path == '/api/directory-parts/'

def test_directory_parts_subdir(
    nested_directories_root_dir: Path,
    nested_directories_client: FlaskClient
):
    response = nested_directories_client.get('/api/directory-parts/subdir1')
    assert response.status_code == 200
    parts = response.json
    assert parts[0]['part'] == nested_directories_root_dir.as_posix()
    assert urlparse(parts[0]['directory-info-url']).path == '/api/directory-info/'
    assert parts[1]['part'] == 'subdir1'
    assert urlparse(parts[1]['directory-info-url']).path == '/api/directory-info/subdir1'

def test_directory_parts_subdir_trailing_slash(
    nested_directories_root_dir: Path,
    nested_directories_client: FlaskClient
):
    response = nested_directories_client.get('/api/directory-parts/subdir1/')
    assert response.status_code == 200
    parts = response.json
    assert parts[0]['part'] == nested_directories_root_dir.as_posix()
    assert urlparse(parts[0]['directory-info-url']).path == '/api/directory-info/'
    assert parts[1]['part'] == 'subdir1'
    assert urlparse(parts[1]['directory-info-url']).path == '/api/directory-info/subdir1'

def test_directory_parts_multiple_subdirs(
    nested_directories_root_dir: Path,
    nested_directories_client: FlaskClient
):
    response = nested_directories_client.get('/api/directory-parts/subdir1/subdir2')
    assert response.status_code == 200
    parts = response.json
    assert parts[0]['part'] == nested_directories_root_dir.as_posix()
    assert urlparse(parts[0]['directory-info-url']).path == '/api/directory-info/'
    assert parts[1]['part'] == 'subdir1'
    assert urlparse(parts[1]['directory-info-url']).path == '/api/directory-info/subdir1'
    assert parts[2]['part'] == 'subdir2'
    assert urlparse(parts[2]['directory-info-url']).path == '/api/directory-info/subdir1/subdir2'

def test_directory_parts_missing_subdir(nested_directories_client: FlaskClient):
    response = nested_directories_client.get('/api/directory-parts/missing-subdir')
    assert response.status_code == 404

def test_directory_parts_on_file(
    nested_directories_root_dir: Path,
    nested_directories_client: FlaskClient
):
    assert (nested_directories_root_dir / 'file.txt').exists()
    response = nested_directories_client.get('/api/directory-parts/file.txt')
    assert response.status_code == 404

# root_dir and test_client fixtures to test the /api/file-info/
# Directory structure is
# root_dir/
#     red-image.jpeg
#     subdir1/text-file.txt
@pytest.fixture(scope="session")
def image_and_text_root_dir(tmp_path_factory: TempPathFactory) -> Path:
    root_dir = tmp_path_factory.mktemp('root-dir')
    img = Image.new('RGB', size=(150,150), color=(255,0,0))
    img.save(root_dir / 'red-image.jpeg')
    (root_dir / 'subdir').mkdir()
    with open(root_dir / 'subdir/text-file.txt', 'w') as f:
        f.write('a text file')
    return root_dir

@pytest.fixture(scope="session")
def image_and_text_client(
    image_and_text_root_dir: Path,
    tmp_path_factory: TempPathFactory
) -> FlaskClient:
    instance_dir = tmp_path_factory.mktemp('instance-dir')
    app = create_test_app(image_and_text_root_dir, instance_dir)
    return app.test_client()

def test_file_info_on_image(
    image_and_text_root_dir: Path,
    image_and_text_client: FlaskClient
):
    img_path = image_and_text_root_dir / 'red-image.jpeg'
    assert img_path.exists()
    img_md5 = get_file_md5(img_path)
    response = image_and_text_client.get('/api/file-info/red-image.jpeg')
    assert response.status_code == 200
    file_info = response.json
    assert urlparse(file_info['file_data_url']).path == f'/api/file-data/{img_md5}.jpeg'
    assert file_info['file_type'] == 'image'
    assert file_info['name'] == 'red-image.jpeg'
    assert file_info['relpath'] == 'red-image.jpeg'
    thumbnail_url = urlparse(file_info['thumbnail_url'])
    assert thumbnail_url.path.startswith('/api/thumbnails/')
    assert thumbnail_url.path.endswith('png')

def test_file_info_on_text_file(
    image_and_text_root_dir: Path,
    image_and_text_client: FlaskClient
):
    text_path = image_and_text_root_dir / 'subdir/text-file.txt'
    assert text_path.exists()
    response = image_and_text_client.get('/api/file-info/subdir/text-file.txt')
    file_info = response.json
    assert file_info['file_data_url'] is None
    assert file_info['file_type'] is None
    assert file_info['name'] == 'text-file.txt'
    assert file_info['relpath'] == 'subdir/text-file.txt'
    assert file_info['st_size'] == len('a text file')
    assert file_info['thumbnail_url'] is None

def test_file_info_on_missing_file(
    image_and_text_root_dir: Path,
    image_and_text_client: FlaskClient
):
    missing_file_path = image_and_text_root_dir / 'missing-file'
    assert not missing_file_path.exists()
    response = image_and_text_client.get('/api/file-info/missing-file')
    assert response.status_code == 404