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

editor = Blueprint('editor', __name__, url_prefix='/edit')

@editor.route('/')
@editor.route('/index')
def index():
    return send_from_directory('static', 'editor/index.html')


