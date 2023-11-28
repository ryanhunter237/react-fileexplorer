from flask import Flask

from fileexplorer.routes import api
from fileexplorer.models import init_database
from fileexplorer.db_builder import build_database_async

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env(prefix='FILEEXPLORER')
    app.config['SUPPORTED_EXTENSIONS'] = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf']#, '.stl']
    app.register_blueprint(api, url_prefix='/api')
    init_database(app)
    build_database_async(app)

    return app