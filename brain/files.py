
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
    send_file,
    session,
    url_for,
)

import os
import io
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
    
    filetype = dirparser.get_item_at_path(filepath)['type']
    
    # Not a displayable filetype. Send out as download.
    if filetype not in ['html', 'txt', 'md']:
        with open(fullpath, 'rb') as fh:
            return send_file(
                     io.BytesIO(fh.read()),
                     attachment_filename=os.path.basename(fullpath),
               )
        # send_from_directory(os.path.dirname(fullpath), os.path.basename(fullpath), as_attachment = True)

    # Still here? Display contents (or stuff it in JSON).
    contents = ''
    f = open(fullpath, 'r')
    contents = f.read()

    if request_wants_json():
        return jsonify({
            'type' : filetype,
            'contents' : contents
            })

    # What happens exactly depends on the file type
 
    if filetype == 'md':
        import markdown
        from flask import Markup
        return Markup(markdown.markdown(content))

    return contents

# Copied from http://flask.pocoo.org/snippets/45/
#
# Why check if json has a higher quality than HTML and not just go with the best match? Because some browsers accept on */* and we don't want to deliver JSON to an ordinary browser.
def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']
