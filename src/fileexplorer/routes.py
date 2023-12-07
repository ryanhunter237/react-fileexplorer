from pathlib import Path

from flask import Blueprint, jsonify, current_app, abort, send_from_directory, url_for

from fileexplorer.models import get_thumbnail_filename, get_data_filename

api = Blueprint('api', __name__)

@api.route('/directory-info/<path:relpath>', methods=['GET'])
def directory_listing(relpath: str):
    if '..' in relpath or '\\' in relpath:
        abort(404)
    return get_directory_listing(relpath)

@api.route('/directory-info/', methods=['GET'])
def rootdir_directory_listing():
    relpath = '.'
    return get_directory_listing(relpath)

def get_directory_listing(relpath: str):
    rootdir = Path(current_app.config['ROOT_DIR'])
    path = rootdir / relpath
    if not path.is_dir():
        abort(404)
    files = []
    directories = []
    for child_path in path.glob('*'):
        child_relpath = child_path.relative_to(rootdir)
        child_data = {'name': child_path.name, 'relpath': child_relpath.as_posix()}
        if child_path.is_file():
            child_data['link'] = url_for(
                'api.file_info',
                relpath=child_relpath.as_posix(),
                _external=True
            )
            files.append(child_data)
        elif child_path.is_dir():
            child_data['link'] = url_for(
                'api.directory_listing',
                relpath=child_relpath.as_posix(),
                _external=True
            )
            directories.append(child_data)
    return jsonify({
        'relpath': relpath,
        'files': files,
        'directories': directories,
        'parts': url_for('api.directory_parts', relpath=relpath, _external=True)
    })

@api.route('/file-info/<path:relpath>', methods=['GET'])
def file_info(relpath: str):
    if '..' in relpath or '\\' in relpath:
        abort(404)
    rootdir = Path(current_app.config['ROOT_DIR'])
    path = rootdir / relpath
    if not path.is_file():
        abort(404)
    return jsonify({
        'relpath': relpath,
        'name': path.name,
        'st_size': path.stat().st_size,
        'file_type': get_file_type(path),
        'thumbnail_url': get_thumbnail_url(path),
        'file_data_url': get_file_data_url(path)
    })

def get_file_type(path: Path) -> str:
    extension = path.suffix.lower()
    if extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        return 'image'
    if extension == '.pdf':
        return 'pdf'
    if extension == '.stl':
        return 'stl'
    return None

def get_thumbnail_url(path: Path) -> str:
    if path.suffix.lower() not in current_app.config['SUPPORTED_EXTENSIONS']:
        return None
    thumbnail_filename = get_thumbnail_filename(path)
    # return something better in these cases?
    if thumbnail_filename in ['processing', 'error']:
        return thumbnail_filename
    return url_for(
        'api.serve_thumbnail',
        filename=thumbnail_filename,
        _external=True
    )

def get_file_data_url(path: Path) -> str:
    data_filename = get_data_filename(path)
    if data_filename is None:
        return None
    return url_for(
        'api.serve_file_data',
        filename=data_filename,
        _external=True
    )

@api.route('/thumbnails/<path:filename>', methods=['GET'])
def serve_thumbnail(filename: str):
    thumbnails_dir = Path(current_app.config['RESOURCES_DIR']) / 'thumbnails'
    return send_from_directory(thumbnails_dir, filename)

@api.route('file-data/<path:filename>', methods=['GET'])
def serve_file_data(filename: str):
    files_dir = Path(current_app.config['RESOURCES_DIR']) / 'files'
    return send_from_directory(files_dir, filename)

@api.route('/directory-parts/<path:relpath>', methods=['GET'])
def directory_parts(relpath: str):
    if '..' in relpath or '\\' in relpath:
        abort(404)
    return get_directory_parts(relpath)

@api.route('/directory-parts/', methods=['GET'])
def rootdir_directory_parts():
    return get_directory_parts('.')

def get_directory_parts(relpath: str):
    rootdir = Path(current_app.config['ROOT_DIR'])
    path = rootdir / relpath
    if not path.is_dir():
        abort(404)
    parts = [{
        'part': rootdir.as_posix(),
        'directory-info-url': url_for('api.rootdir_directory_listing', _external=True)
    }]
    if path == rootdir:
        return jsonify(parts)
    current_path = rootdir
    for part in path.relative_to(rootdir).parts:
        current_path = current_path / part
        current_relpath = current_path.relative_to(rootdir)
        parts.append({
            'part': part,
            'directory-info-url': url_for(
                'api.directory_listing',
                relpath=current_relpath.as_posix(),
                _external=True
            )
        })
    return jsonify(parts)