from flask import Flask

from fileexplorer.routes import api
from fileexplorer.models import init_database
from fileexplorer.db_builder import build_database_async

def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_prefixed_env(prefix='FILEEXPLORER')
    app.config['SUPPORTED_EXTENSIONS'] = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf', '.stl']
    app.register_blueprint(api, url_prefix='/api')
    init_database(app)
    testing = app.config.get('TESTING', False)
    build_database_async(app, testing)

    return app
