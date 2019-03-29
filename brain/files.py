
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

@files.route('/create', methods=['POST'])
def create_file():

    filepath = request.form['filepath']

    dirparser = dirparse.DirParse(current_app.config['filedir'])

    if dirparser.get_item_at_path(filepath) != None:
        current_app.logger.debug("Attempt to create already existing file" + filepath)
        abort(409)

    fullpath = os.path.join(current_app.config['filedir'], filepath)

    f = open(fullpath, 'w')
    f.write('')

    return redirect('/files/view/' + filepath, code=303)


@files.route('/save/<path:filepath>', methods=['PUT', 'POST'])
def save_file(filepath):
    dirparser = dirparse.DirParse(current_app.config['filedir'])

    if dirparser.get_item_at_path(filepath) == None:
        current_app.logger.debug("Attempt to save non-existent path " + filepath)
        abort(404)

    fullpath = os.path.join(current_app.config['filedir'], filepath)
    if not os.path.isfile(fullpath):
        current_app.logger.debug("Requested path does not exist on filesystem: " + fullpath)
        abort(404)

    filecontents = request.form['filecontents']

    f = open(fullpath, 'w')
    f.write(filecontents)

    return redirect('/files/view/' + filepath, code=303)

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
    
    contents = ''
    f = open(fullpath, 'r')
    contents = f.read()
    filetype = dirparser.get_item_at_path(filepath)['type']

    if request_wants_json():
        return jsonify({
            'type' : filetype,
            'contents' : contents
            })

    # What happens exactly depends on the file type
    filetype = dirparser.get_item_at_path(filepath)['type']
    if filetype == 'html':
        f = open(fullpath, 'r')
        return f.read()
 
    if filetype == 'md':
        import markdown
        from flask import Markup
        f = open(fullpath, 'r')
        content = f.read()
        return Markup(markdown.markdown(content))
        
    #

    # We don't know the file type. Send out as download.
    return send_from_directory(current_app.config['filedir'], filepath)
    f = open(fullpath, 'r')
    # return jsonify(f.read())
    return f.read()



# Copied from http://flask.pocoo.org/snippets/45/
#
# Why check if json has a higher quality than HTML and not just go with the best match? Because some browsers accept on */* and we don't want to deliver JSON to an ordinary browser.
def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']
