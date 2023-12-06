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

# fixtures to test /api/directory-parts/  
# Directory structure is
# root_dir/subdir1/subdir2/file.txt
@pytest.fixture(scope="session")
def root_dir_1(tmp_path_factory: TempPathFactory) -> Path:
    root_dir = tmp_path_factory.mktemp('root-dir')
    (root_dir / 'subdir1/subdir2').mkdir(parents=True)
    (root_dir / 'file.txt').touch()
    return root_dir

@pytest.fixture(scope="session")
def client_1(
    root_dir_1: Path,
    tmp_path_factory: TempPathFactory
) -> FlaskClient:
    instance_dir = tmp_path_factory.mktemp('instance-dir')
    app = create_test_app(root_dir_1, instance_dir)
    return app.test_client()

def test_directory_parts_root_dir(
    root_dir_1: Path,
    client_1: FlaskClient
):
    response = client_1.get('/api/directory-parts/')
    assert response.status_code == 200
    parts = response.json
    assert parts[0]['part'] == root_dir_1.as_posix()
    assert urlparse(parts[0]['directory-info-url']).path == '/api/directory-info/'

def test_directory_parts_redirect(client_1: FlaskClient):
    response = client_1.get('/api/directory-parts')
    assert response.status_code == 308
    redirect_location = response.headers['Location']
    assert urlparse(redirect_location).path == '/api/directory-parts/'

def test_directory_parts_subdir(
    root_dir_1: Path,
    client_1: FlaskClient
):
    response = client_1.get('/api/directory-parts/subdir1')
    assert response.status_code == 200
    parts = response.json
    assert parts[0]['part'] == root_dir_1.as_posix()
    assert urlparse(parts[0]['directory-info-url']).path == '/api/directory-info/'
    assert parts[1]['part'] == 'subdir1'
    assert urlparse(parts[1]['directory-info-url']).path == '/api/directory-info/subdir1'

def test_directory_parts_subdir_trailing_slash(
    root_dir_1: Path,
    client_1: FlaskClient
):
    response = client_1.get('/api/directory-parts/subdir1/')
    assert response.status_code == 200
    parts = response.json
    assert parts[0]['part'] == root_dir_1.as_posix()
    assert urlparse(parts[0]['directory-info-url']).path == '/api/directory-info/'
    assert parts[1]['part'] == 'subdir1'
    assert urlparse(parts[1]['directory-info-url']).path == '/api/directory-info/subdir1'

def test_directory_parts_multiple_subdirs(
    root_dir_1: Path,
    client_1: FlaskClient
):
    response = client_1.get('/api/directory-parts/subdir1/subdir2')
    assert response.status_code == 200
    parts = response.json
    assert parts[0]['part'] == root_dir_1.as_posix()
    assert urlparse(parts[0]['directory-info-url']).path == '/api/directory-info/'
    assert parts[1]['part'] == 'subdir1'
    assert urlparse(parts[1]['directory-info-url']).path == '/api/directory-info/subdir1'
    assert parts[2]['part'] == 'subdir2'
    assert urlparse(parts[2]['directory-info-url']).path == '/api/directory-info/subdir1/subdir2'

def test_directory_parts_missing_subdir(client_1: FlaskClient):
    response = client_1.get('/api/directory-parts/missing-subdir')
    assert response.status_code == 404

def test_directory_parts_on_file(
    root_dir_1: Path,
    client_1: FlaskClient
):
    assert (root_dir_1 / 'file.txt').exists()
    response = client_1.get('/api/directory-parts/file.txt')
    assert response.status_code == 404

# fixtures to test /api/file-info/
# Directory structure is
# root_dir/
#     red-image.jpeg
#     subdir1/text-file.txt
@pytest.fixture(scope="session")
def root_dir_2(tmp_path_factory: TempPathFactory) -> Path:
    root_dir = tmp_path_factory.mktemp('root-dir')
    img = Image.new('RGB', size=(150,150), color=(255,0,0))
    img.save(root_dir / 'red-image.jpeg')
    (root_dir / 'subdir').mkdir()
    with open(root_dir / 'subdir/text-file.txt', 'w') as f:
        f.write('a text file')
    return root_dir

@pytest.fixture(scope="session")
def client_2(
    root_dir_2: Path,
    tmp_path_factory: TempPathFactory
) -> FlaskClient:
    instance_dir = tmp_path_factory.mktemp('instance-dir')
    app = create_test_app(root_dir_2, instance_dir)
    return app.test_client()

def test_file_info_on_image(
    root_dir_2: Path,
    client_2: FlaskClient
):
    img_path = root_dir_2 / 'red-image.jpeg'
    assert img_path.exists()
    img_md5 = get_file_md5(img_path)
    response = client_2.get('/api/file-info/red-image.jpeg')
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
    root_dir_2: Path,
    client_2: FlaskClient
):
    text_path = root_dir_2 / 'subdir/text-file.txt'
    assert text_path.exists()
    response = client_2.get('/api/file-info/subdir/text-file.txt')
    file_info = response.json
    assert file_info['file_data_url'] is None
    assert file_info['file_type'] is None
    assert file_info['name'] == 'text-file.txt'
    assert file_info['relpath'] == 'subdir/text-file.txt'
    assert file_info['st_size'] == len('a text file')
    assert file_info['thumbnail_url'] is None

def test_file_info_on_missing_file(
    root_dir_2: Path,
    client_2: FlaskClient
):
    missing_file_path = root_dir_2 / 'missing-file'
    assert not missing_file_path.exists()
    response = client_2.get('/api/file-info/missing-file')
    assert response.status_code == 404

# fixtures to test /api/directory-info/
# Directory structure is
# root_dir/
#     file1.txt
#     subdir1/file2.txt
#     subdir2/
#         file3.txt
#         subdir3/
@pytest.fixture(scope="session")
def root_dir_3(tmp_path_factory: TempPathFactory) -> Path:
    root_dir = tmp_path_factory.mktemp('root-dir')
    (root_dir / 'subdir1').mkdir()
    (root_dir / 'subdir2').mkdir()
    (root_dir / 'subdir2/subdir3').mkdir()
    (root_dir / 'file1.txt').touch()
    (root_dir / 'subdir1/file2.txt').touch()
    (root_dir / 'subdir2/file3.txt').touch()
    return root_dir

@pytest.fixture(scope="session")
def client_3(
    root_dir_3: Path,
    tmp_path_factory: TempPathFactory
) -> FlaskClient:
    instance_dir = tmp_path_factory.mktemp('instance-dir')
    app = create_test_app(root_dir_3, instance_dir)
    return app.test_client()

def test_directory_info_root_dir(
    root_dir_3: Path,
    client_3: FlaskClient
):
    response = client_3.get('/api/directory-info/')
    assert response.status_code == 200
    directory_info = response.json
    directories = directory_info['directories']
    assert len(directories) == 2
    for d in directories:
        name = d['name']
        assert urlparse(d['link']).path == f'/api/directory-info/{name}'
    directory_names = [d['name'] for d in directories]
    expected_directory_names = [p.name for p in root_dir_3.glob('*') if p.is_dir()]
    assert sorted(directory_names) == sorted(expected_directory_names)
    files = directory_info['files']
    assert len(files) == 1
    assert files[0]['name'] == 'file1.txt'
    assert urlparse(files[0]['link']).path == '/api/file-info/file1.txt'
    parts = directory_info['parts']
    assert urlparse(parts).path == '/api/directory-parts/.'
    assert directory_info['relpath'] == '.'

def test_directory_info_redirect(client_3: FlaskClient):
    response = client_3.get('/api/directory-info')
    assert response.status_code == 308
    redirect_location = response.headers['Location']
    assert urlparse(redirect_location).path == '/api/directory-info/'

def test_directory_info_subdir2(client_3: FlaskClient):
    response = client_3.get('/api/directory-info/subdir2')
    assert response.status_code == 200
    directory_info = response.json
    directories = directory_info['directories']
    assert len(directories) == 1
    assert directories[0]['name'] == 'subdir3'
    assert urlparse(directories[0]['link']).path == '/api/directory-info/subdir2/subdir3'
    files = directory_info['files']
    assert len(files) == 1
    assert files[0]['name'] == 'file3.txt'
    assert urlparse(files[0]['link']).path == '/api/file-info/subdir2/file3.txt'
    parts = directory_info['parts']
    assert urlparse(parts).path == '/api/directory-parts/subdir2'
    assert directory_info['relpath'] == 'subdir2'

def test_directory_info_subdir3(client_3: FlaskClient):
    response = client_3.get('/api/directory-info/subdir2/subdir3')
    assert response.status_code == 200
    directory_info = response.json
    assert len(directory_info['directories']) == 0
    assert len(directory_info['files']) == 0
    parts = directory_info['parts']
    assert urlparse(parts).path == '/api/directory-parts/subdir2/subdir3'
    assert directory_info['relpath'] == 'subdir2/subdir3'

def test_directory_info_missing_subdir(client_3: FlaskClient):
    response = client_3.get('/api/directory-info/missing-subdir')
    assert response.status_code == 404