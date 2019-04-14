
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

@files.route('/delete/<path:filepath>', methods=['DELETE'])
def delete_file(filepath):
    dirparser = dirparse.DirParse(current_app.config['filedir'])

    if dirparser.get_item_at_path(filepath) == None:
        current_app.logger.debug("Attempt to delete non-existent path " + filepath)
        return ''

    fullpath = os.path.join(current_app.config['filedir'], filepath)
    if not os.path.isfile(fullpath):
        current_app.logger.debug("Requested path to delete does not exist on filesystem: " + fullpath)
        return ''

    os.remove(fullpath)

    return ''

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

@files.route('/rename/<path:filepath>', methods=['POST'])
def rename_file(filepath):

    new_title = request.form['newtitle']
    new_title = " ".join(new_title.strip().split())

    dirparser = dirparse.DirParse(current_app.config['filedir'])

    if dirparser.get_item_at_path(filepath) == None:
        current_app.logger.debug("Attempt to save non-existent path " + filepath)
        abort(404)

    fullpath = os.path.join(current_app.config['filedir'], filepath)
    if not os.path.isfile(fullpath):
        current_app.logger.debug("Requested path does not exist on filesystem: " + fullpath)
        abort(404)

    filetype = dirparser.get_item_at_path(filepath)['type']
   
    new_filedir, Nil = os.path.split(
            os.path.join(current_app.config['filedir'], filepath))
    
    new_fullpath = os.path.join(new_filedir, new_title + '.' + filetype)

    if os.path.exists(new_fullpath):
        current_app.logger.debug('Denied request to move ' + fullpath + ' to existing file ' + new_fullpath)
        abort(409)

    os.rename(fullpath, new_fullpath)

    # No redirect as that makes it impossible to load the new file as raw data.
    # Instead just provide the url to redirect to.
    return new_title + '.' + filetype
    # return redirect('/files/view/' + new_title + '.' + filetype, code=303 )


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
    # Not sure why but occasionally garbage utf ends up in these files.
    # If that happens, it's better to just send out the file without raising
    # a stink.
    f = open(fullpath, 'r', encoding='utf-8',
                 errors='ignore')
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
        return Markup(markdown.markdown(contents))

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
