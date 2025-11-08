"""
Music Fansite
Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 8th November 2025
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

# discover home page
@app.route('/discover/')
def discover_home():
    kind = request.args.get('kind')
    if kind:
        return redirect(url_for('discover_kind', kind=kind))
    flash("You need to make a selection")
    return render_template('discover.html') 

# brings the user to the correct form to discover new music
@app.route('/discover/<kind>', methods=['GET', 'POST'])
def discover_kind(kind):
    if kind == 'artist':
        if request.method == 'POST':
            genre = request.form.get('genre')
            num_rating = request.form.get('num_rating')
            artists = discover_artists(conn, genre, num_rating)
            return render_template('discover-artist-results.html',genre=genre,num_rating=num_rating, artists=artists)
        return render_template('discover-artist.html')
    elif kind == 'album':
        if request.method == 'POST':
            genre = request.form.get('genre')
            num_rating = request.form.get('num_rating')
            albums = discover_albums(conn, genre, num_rating)
            return render_template('discover-album-results.html',genre=genre,num_rating=num_rating, albums=albums)
        return render_template('discover-album.html')
    elif kind == 'beef':
        if request.method == 'POST':
            artist = request.form.get('artist')
            genre = request.form.get('genre')
            beefs = discover_beefs(conn, artist, genre)
            return render_template('discover-beef-results.html',artist=artist, genre=genre, beefs=beefs)
        return render_template('discover-beef.html')


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