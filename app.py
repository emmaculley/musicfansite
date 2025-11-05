"""
Music Fansite
Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 5th November 2025
"""


from flask import (Flask, render_template, url_for, request,
                   redirect)
app = Flask(__name__)

import cs304dbi as dbi
import music


print(dbi.conf('musicfan_db'))


@app.route('/')
def index():
    return render_template('base.html', page_title="Main Page")



# pages for individual artists
@app.route('/artist/<id>/')
def artist(id):
    conn = dbi.connect()
    artist = music.get_artist(conn, id)
    return render_template('artist.html', artist=artist)

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