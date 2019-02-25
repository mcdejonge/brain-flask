
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for,
    jsonify,
    abort
)

import os

files = Blueprint('files', __name__, url_prefix='/files')

@files.route('/')
@files.route('/index')
def index():
    contents = current_app.config['dirparser'].get_contents()
    return jsonify(contents)

@files.route('/view/<path:filepath>', methods=['GET'])
def process_file(filepath):
    fullpath = os.path.join(current_app.config['filedir'], filepath)
    if not os.path.isfile(fullpath):
        current_app.logger.debug("Request for non-existent path " + fullpath)
        abort(404)

    # show the subpath after /path/
    return 'Subpath %s' % filepath




