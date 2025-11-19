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
        if user and password == music.get_password(conn, email):
            session['user_id'] = user['userID']
            session['user_email'] = user['user_email']
            session['fname'] = user['fname']
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
        user = music.create_user(conn, email, fname, lname, password)
        print (f'{user=}')
        session['user_id'] = user['userID']
        session['user_email'] = email
        session['fname'] = fname
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
            artists = music.discover_artists(conn, genre, num_rating)
            return render_template('discover-artist-results.html',genre=genre,num_rating=num_rating, artists=artists)
        genres = music.get_genres(conn)
        return render_template('discover-artist.html', genres=genres)
    elif kind == 'album':
        if request.method == 'POST':
            genre = request.form.get('genre')
            num_rating = request.form.get('num_rating')
            albums = music.discover_albums(conn, genre, num_rating)
            return render_template('discover-album-results.html',genre=genre,num_rating=num_rating, albums=albums)
        genres = music.get_genres(conn)
        return render_template('discover-album.html', genres=genres)
    elif kind == 'beef':
        if request.method == 'POST':
            artist = request.form.get('artist')
            genre = request.form.get('genre')
            beefs = music.discover_beefs(conn, artist, genre)
            return render_template('discover-beef-results.html',artist=artist, genre=genre, beefs=beefs)
        genres = music.get_genres(conn)
        return render_template('discover-beef.html', genres=genres)

# pages for individual artists
@app.route('/artist/<id>/', methods = ['GET', 'POST'])
def artist(id):
    conn = dbi.connect()
    artist = music.get_artist(conn, id)
    beefs = music.get_beef(conn, artist[0]['artistID'])
    if request.method == 'GET':
        return render_template('artist.html', artist=artist, beefs=beefs)
    else:
        form_data = request.form
        music.insert_rating(conn, form_data, id)
        music.update_artist_rating(conn, id)
        artist_w_current_rating = music.get_artist(conn, id) # change to better name later
        # need to get the artist again so that their new rating gets rendered on their page
        return render_template('artist.html', artist=artist_w_current_rating, beefs=beefs)
        


# going to be used for the music form
@app.route('/add-music/')
def add_music():
    type = request.args['add']
    return render_template('add.html') 


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
                music.insert_to_forums(conn, type, title, user_id)
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


@app.route('/forum/<forum_id>', methods=['GET', 'POST'])
def view_forum(forum_id):
    conn = dbi.connect()
    if request.method == 'POST':
        content = request.form.get('content')
        user_id = session.get('user_id')
        if not user_id:
            flash("You must be logged in to post.")
            return redirect(url_for('login'))
        if content:
            music.insert_post(conn, forum_id, user_id, content)
        else:
            flash("Post cannot be empty.")
        return redirect(url_for('view_forum', forum_id=forum_id))
    forum = music.get_forum(conn, forum_id)
    posts = music.get_posts(conn, forum_id)
    return render_template('view-forum.html', forum=forum, posts=posts)



#is there a way for the user to be able to like type in artist (and the query )
#insert beef form
@app.route('/insertbeef/', methods= ['GET', 'POST'])
def insertbeef():
    conn = dbi.connect()
    if request.method == 'GET':
        all_artists = music.get_artists(conn)
        return render_template('beef_form.html', artists=all_artists)

        # POST: get selected tt
    artist1 = request.form.get('artist1')
    artist2 = request.form.get('artist2')


    if artist1 == 'none' or artist2 == 'none':
        flash("Please artists that have beefed.")
        artists = music.get_artists(conn)
        return render_template('beef_form.html', artists=all_artists)

    context = request.form.get('reason')
    side = request.form.get('side')   # either "artist1" or "artist2"
    countArtist1 = 1 if side == "artist1" else 0
    countArtist2 = 1 if side == "artist2" else 0
    bid = music.create_beef(conn, artist1, artist2, context, countArtist1, countArtist2)
    fname = session.get('fname')   # retrieve stored name
    flash(f"Beef form was submitted! Thank you {fname}")
    return redirect(url_for('beef_page', bid=bid))


@app.route('/beef/<int:bid>', methods=['GET'])
def beef_page(bid):
    conn = dbi.connect()

    beef = music.get_beef(conn, bid)  # assume this returns a dict with keys like artist1_id, artist2_id, countArtist1, countArtist2, context, approved
    approval = beef['approved']
    #in the HTML, print out the approval status in the webpage

    if not beef:
        flash("Beef not found!")
        return redirect(url_for('index'))

    # Fetch artist details
    artist1 = music.get_artist(conn, beef['artist1'])  # returns dict with name, etc.
    artist2 = music.get_artist(conn, beef['artist2'])

    return render_template(
        'beef_page.html',
        beef=beef,
        artist1=artist1,
        artist2=artist2
    )




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