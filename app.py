"""
Music Fansite
Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 5th November 2025
"""


from flask import (Flask, render_template, url_for, request,
                   redirect)
app = Flask(__name__)

import cs304dbi as dbi



print(dbi.conf('musicfan_db'))

@app.route('/')
def index():
    return render_template('base.html', page_title="Main Page")


@app.route('/discover/')
def discover():
    '''
    Returns the rendered page for the type inputted to the discover form.

    Args:
        None
    Return:
        String of the rendered template -> str
    '''
    query_type = request.args.get('kind')
    conn = dbi.connect()

    if query_type == 'artist':
        return render_template('discover-artist.html')

    if query_type == 'album':
        return render_template('discover-album.html')   

    if query_type == 'beef':
        return render_template('discover-beef.html')   


# pages for individual artists
@app.route('/artist/<name>/')
def artist(name):
    conn = dbi.connect()
    return render_template('artist.html', page_title=name)

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)