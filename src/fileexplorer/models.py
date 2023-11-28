from pathlib import Path
import sqlite3

from flask import Flask

DATABASE_PATH = None

def init_database(app: Flask):
    """Set DATABASE_PATH from app.config"""
    global DATABASE_PATH 
    DATABASE_PATH = app.config['DATABASE_PATH']
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

def get_db_connection() -> sqlite3.Connection:
    """Get connection to the file explorer sqlite database"""
    if DATABASE_PATH is None:
        raise RuntimeError('DATABASE_PATH has not been set')
    return sqlite3.connect(DATABASE_PATH)

def create_tables():
    conn = get_db_connection()
    conn.execute('DROP TABLE IF EXISTS thumbnails')
    conn.execute('CREATE TABLE IF NOT EXISTS thumbnails (file_path STR, thumbnail_file STR)')
    conn.execute('CREATE TABLE IF NOT EXISTS data_files (file_path STR, data_file STR)')
    conn.close()    

def normalize_path(path: str|Path) -> str:
    """Normalize a path for insertion into or querying the database"""
    return Path(path).resolve().as_posix()

def insert_thumbnail(file_path: str|Path, thumbnail_filename: str):
    """Insert a thumbnail filename for the given file_path and commit to the database"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO thumbnails (file_path, thumbnail_file) VALUES (?,?)',
        (normalize_path(file_path), thumbnail_filename)
    )
    conn.commit()
    conn.close()

def get_thumbnail_filename(file_path: str|Path) -> str|None:
    """Return
        the filename of the thumbnail in config.resources_dir for computed thumbnails
        'processing' if the thumbnail is not computed yet (file_path missing from table)
        'error' if there was an error computing the thumbnail (file_path exists, but no thumbnail)
    """
    conn = get_db_connection()
    result = conn.execute(
        'SELECT thumbnail_file FROM thumbnails WHERE file_path = ?',
        (normalize_path(file_path),)
    ).fetchone()
    if result is None:
        return 'processing'
    if result[0] is None:
        return 'error'
    else:
        return result[0]

def thumbnail_exists_for_file(file_path: str|Path) -> bool:
    conn = get_db_connection()
    result = conn.execute(
        'SELECT EXISTS (SELECT 1 FROM thumbnails WHERE file_path = ?)',
        (normalize_path(file_path),)
    ).fetchone()
    return result[0]

def insert_data_file(file_path: str|Path, data_filename: str):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO data_files (file_path, data_file) VALUES (?,?)',
        (normalize_path(file_path), data_filename)
    )
    conn.commit()
    conn.close()

def get_data_filename(file_path: str|Path) -> str|None:
    conn = get_db_connection()
    result = conn.execute(
        'SELECT data_file FROM data_files WHERE file_path = ?',
        (normalize_path(file_path),)
    ).fetchone()
    if result is None:
        return None
    else:
        return result[0]