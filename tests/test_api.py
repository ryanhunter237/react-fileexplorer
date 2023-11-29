from pathlib import Path
from urllib.parse import urlparse

from flask import Flask
from flask.testing import FlaskClient 
import pytest
from pytest import TempPathFactory

from fileexplorer import create_app

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

@pytest.fixture(scope="session")
def nested_directories_root_dir(tmp_path_factory: TempPathFactory) -> Path:
    root_dir = tmp_path_factory.mktemp('root-dir')
    (root_dir / 'subdir1/subdir2/subdir3').mkdir(parents=True)
    return root_dir

@pytest.fixture(scope="session")
def nested_directories_client(
    nested_directories_root_dir: Path,
    tmp_path_factory: TempPathFactory
) -> tuple[Path, FlaskClient]:
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


# @pytest.fixture(scope="session")
# def root_dir(tmp_path_factory: TempPathFactory):
#     temp_dir = tmp_path_factory.mktemp("root_dir")
#     (temp_dir / 'subdir1/subdir2').mkdir(parents=True)
#     red_image = Image.new('RGB', size=(150,150), color=(255,0,0))
#     red_image.save(temp_dir / 'subdir1/red_image.png')
#     for i in range(5):
#         path = temp_dir / f'subdir1/subdir2/file{i}.txt'
#     yield temp_dir

# @pytest.fixture(scope="session")
# def app(root_dir: Path, tmp_path_factory: TempPathFactory):
#     instance_dir = tmp_path_factory.mktemp('instance')
#     resources_dir = instance_dir / 'resources'
#     database_path = instance_dir / 'files.db'
#     test_config = {
#         "TESTING": True,
#         "ROOT_DIR": root_dir.as_posix(),
#         "RESOURCES_DIR": resources_dir.as_posix(),
#         "DATABASE_PATH": database_path.as_posix()
#     }
#     app = create_app(test_config)
#     yield app

# @pytest.fixture(scope="session")
# def client(app: Flask) -> FlaskClient:
#     return app.test_client()
