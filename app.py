"""
Music Fansite
Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 12th November 2025
"""

from flask import (Flask, render_template, url_for, request,
                   redirect, session, flash)

app = Flask(__name__)

import secrets
import cs304dbi as dbi
import music

app.secret_key = secrets.token_hex()

print(dbi.conf('musicfan_db'))


@app.route('/')
def index():
    return render_template('main.html', page_title="Main Page")

#login for users -- if they have an account
@app.route('/login/', methods=['GET', 'POST'])
def login():
    conn = dbi.connect()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = music.get_user_by_email(conn, email)
        if user and password == get_password(conn, email):
            session['user_id'] = user['userID']
            session['user_email'] = user['user_email']
            session['fname'] = user['fname']
            flash("You have been successfully logged in!")
            return redirect(url_for('index'))
        else:
            return render_template('signup.html', email=email)
    return render_template('login.html')

# signup for users -- need to make an account
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    conn = dbi.connect()
    if request.method == 'POST':
        email = request.form.get('email')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        password = request.form.get('password')
        music.add_user(conn, email, fname, lname, password)
        session['user_id'] = user['userID']
        session['user_email'] = email
        session['fname'] = fname
        flash("Your account was created! You are now logged in!")
        return redirect(url_for('index'))
    return render_template('signup.html')

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
    conn = dbi.connect()
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

@app.route('/forums/')
def forums_home():
    type = request.args.get('type')
    if type:
        return redirect(url_for('forums_type', type=type))
    flash("You need to make a selection")
    return render_template('forums.html') 

@app.route('/forums/<type>', methods=['GET', 'POST'])
def forums_type(type):
    conn = dbi.connect()
    if type == 'music':
        if request.method == 'POST': 
            # want to select from the forums
            # or make a new forum
            return render_template('forum-artist-results.html',genre=genre,num_rating=num_rating, artists=artists)
        return render_template('forum-artist.html')
    elif type == 'explore':
        if request.method == 'POST':
            title = request.form.get('title')
            user_id = session.get('user_id')
            if title:
                insert_to_forums(conn, type, title, user_id)
            else:
                flash("Forum title required!")
        forums = music.load_forums(conn, type)
        return render_template('forums-explore.html', type=type, forums=forums)
    elif type == 'beef':
        if request.method == 'POST':
            # want to select from the forums
            # or make a new forum
            return render_template('forum-beef-results.html',artist=artist, genre=genre, beefs=beefs)
        return render_template('forum-beef.html')


@app.route('/forum/<forum_id>')
def view_forum(forum_id):
    conn = dbi.connect()
    forum = get_forum(conn, forum_id)
    posts = get_posts(conn, forum_id)
    return render_template('view-forum.html', forum=forum, posts=posts)


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