from flask import Flask
from flask import g

import os
import configparser

from flask import jsonify
from flask import abort 
import logging

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.logger.setLevel(logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(os.path.join(app.instance_path, 'application.cfg'))

    if not config.has_section('DEFAULTS'):
        app.logger.error("Config does not have the required DEFAULTS section.")
        abort(500)
    if not config.has_option('DEFAULTS', 'filedir'):
        app.logger.error("Config does not have the required filedir setting in the DEFAULTS section.")
        abort(500)

    with app.app_context():
        app.config['filedir'] = config.get('DEFAULTS', 'filedir')

    from . import files
    app.register_blueprint(files.files)

    

    return app
