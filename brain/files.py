
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

import os
from brain import dirparse


files = Blueprint('files', __name__, url_prefix='/files')

@files.route('/')
@files.route('/index')
def index():
    dirparser = dirparse.DirParse(current_app.config['filedir'])
    contents = dirparser.get_contents()
    return jsonify(contents)

@files.route('/view/<path:filepath>', methods=['GET'])
def get_file(filepath):

    dirparser = dirparse.DirParse(current_app.config['filedir'])

    if dirparser.get_item_at_path(filepath) == None:
        current_app.logger.debug("Request for non-existent path " + filepath)
        abort(404)

    fullpath = os.path.join(current_app.config['filedir'], filepath)
    if not os.path.isfile(fullpath):
        current_app.logger.debug("Requested path does not exist on filesystem: " + fullpath)
        abort(404)

    return send_from_directory(current_app.config['filedir'], filepath)
    f = open(fullpath, 'r')
    # return jsonify(f.read())
    return f.read()





