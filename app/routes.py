from app import app

from app.braindir import BrainDir
from flask import jsonify
from flask import abort 

import os
import configparser

@app.route('/')
@app.route('/index')
def index():
    return "Hello world!"

@app.route('/files')
def files():
    config = configparser.ConfigParser()
    config.read(os.path.join(app.instance_path, 'application.cfg'))

    if not config.has_section('DEFAULTS'):
        print("Config does not have the required DEFAULTS section.")
        abort(500)
    if not config.has_option('DEFAULTS', 'filedir'):
        print("Config does not have the required filedir setting in the DEFAULTS section.")
        abort(500)

    braindir = BrainDir(config.get('DEFAULTS', 'filedir'))
    contents = braindir.get_contents()
    return jsonify(contents)



