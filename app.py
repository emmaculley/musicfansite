"""
Music Fansite
Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 25th November 2025
"""

from flask import (Flask, render_template, url_for, request,
                   redirect, session, flash)

app = Flask(__name__)

import secrets
import cs304dbi as dbi
import music
import bcrypt
from pymysql import IntegrityError

# for flashing
app.secret_key = secrets.token_hex()

print(dbi.conf('musicfan_db'))

# The main page of our site
@app.route('/')
def index():
    return render_template('main.html', page_title="Main Page")

#login for users -- if they have an account
@app.route('/login/', methods=['GET', 'POST'])
def login():
    conn = dbi.connect()
    if request.method == 'POST':
        # look up user's email and password in db
        email = request.form.get('email')
        password = request.form.get('password')
        user = music.get_user_by_email(conn, email)

        # if they put in an email that isn't in the db:
        if not user:
            flash("Login incorrect. Try again or sign up.")
            return render_template('signup.html', email=email, page_title='Signup')
        
        # check their passord:
        stored_hash = user['password'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            session['user_id'] = user['userID']
            session['user_email'] = user['user_email']
            session['fname'] = user['fname']
            return redirect(url_for('index'))
        else:
            flash("Login incorrect. Try again or sign up.")
            return render_template('signup.html', email=email, page_title='Signup')
    
    # if this is a GET request, render page as normal
    return render_template('login.html', page_title='Login')

# signup for users -- for if they need to make an account
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    conn = dbi.connect()
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            password = request.form.get('password')
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            stored = hashed.decode('utf-8')
            # add their info to the user table:
            user = music.create_user(conn, email, fname, lname, stored)
            session['user_id'] = user['userID']
            session['user_email'] = email
            session['fname'] = fname
            return redirect(url_for('index'))
        except IntegrityError:
            flash('That email is already associated with an account.')
            return redirect(url_for('login'))
    return render_template('signup.html', page_title='Signup')


# Discover page, where users can choose the type of thing they want to 
# discover - albums, artists, or beef.
@app.route('/discover/')
def discover_home():
    kind = request.args.get('kind')
    if kind:
        return redirect(url_for('discover_kind', kind=kind))
<<<<<<< HEAD
    
=======
>>>>>>> 88c1a086b9e7804508ae03aed2bad60809df758a
    return render_template('discover.html') 

# brings the user to the correct form to discover what they're looking
# for (artists, albums, or beefs)
@app.route('/discover/<kind>', methods=['GET', 'POST'])
def discover_kind(kind):
    conn = dbi.connect()
    if kind == 'artist':
        if request.method == 'POST':
            genre = request.form.get('genre')
            num_rating = request.form.get('num_rating')
            # user selects genre and # of total ratings they want the 
            # artist to have. we make sure artists of their category exist 
            artists = music.discover_artists(conn, genre, num_rating)
            if not artists:
                flash("There are no artists in this category.")
                return redirect(url_for('discover_kind', kind=kind))
            return render_template('discover-artist-results.html',genre=genre,num_rating=num_rating, artists=artists, page_title='Artists to Discover')
        genres = music.get_genres(conn)
        return render_template('discover-artist.html', genres=genres, page_title='Discover Artists')
    elif kind == 'album':
        if request.method == 'POST':
            genre = request.form.get('genre')
            num_rating = request.form.get('num_rating')
            # make sure there are albums in their category
            albums = music.discover_albums(conn, genre, num_rating)
            if not albums:
                flash("There are no albums in this category.")
                return redirect(url_for('discover_kind', kind=kind))
            return render_template('discover-album-results.html',genre=genre,num_rating=num_rating, albums=albums, page_title='Albums to Discover')
        genres = music.get_genres(conn)
        return render_template('discover-album.html', genres=genres, page_title='Discover Albums')
    elif kind == 'beef':
        if request.method == 'POST':
            artist = request.form.get('artist')
            # 'artist' is their id. also need to get their name to display on the page
            artistInfo =  music.get_artist_one(conn, artist)
            artistName = artistInfo['name']
            # make sure there are beefs involving that artist
            beefs = music.discover_beefs(conn, artist)
            if not beefs:
                flash("This artist has no beefs.")
                return redirect(url_for('discover_kind', kind=kind))
            for beef in beefs:
                # get the artist IDs involved
                artist1 = beef["artist1"]
                artist2 = beef["artist2"]
                #get artist1's name
                artist1Info = music.get_artist_one(conn, artist1)
                artist1Name = artist1Info['name']
                # get artist2's name
                artist2Info = music.get_artist_one(conn, artist2)
                artist2Name = artist2Info['name']
                # add names to the beef dict so they can be displayed on the 'beefs to explore'
                beef['artist1Name'] = artist1Name
                beef['artist2Name'] = artist2Name
            return render_template('discover-beef-results.html',artist=artistName, beefs=beefs, page_title='Beefs to Discover')
        genres = music.get_genres(conn)
        artists = music.get_artists(conn)
        return render_template('discover-beef.html', genres=genres, artists=artists, page_title='Discover Beefs')

# pages for individual artists
@app.route('/artist/<id>/', methods = ['GET', 'POST'])
def artist(id):
    conn = dbi.connect()
    artist = music.get_artist(conn, id)
    beefs = music.get_beef_names(conn, id)
    if beefs == None:
        beefs = {}
    if request.method == 'GET':
        for beef in beefs:
            # add the beef ID to the beef, so we can put a link to it
            artistID = artist[0]['artistID']
            beefID = music.get_beef_id(conn, artistID)
            beef['beefID'] = beefID['bid']
        return render_template('artist.html', artist=artist, beefs=beefs, page_title=artist[0]['name'])
    else:
        form_data = request.form
        if 'user_id' in session:
            user_id = session['user_id']
            artistID = artist[0]['artistID']
            potential_rating = music.check_ratings(conn, user_id, artistID)
            if potential_rating == None:
                # if this user hasn't rated this artist yet
                music.insert_rating(conn, form_data, id, user_id)
                music.update_artist_rating(conn, id)
                artist_w_current_rating = music.get_artist(conn, id) # change to better name later
                # need to get the artist again so that their new rating gets rendered on their page
                return render_template('artist.html', artist=artist_w_current_rating, beefs=beefs, page_title=artist[0]['name'])
            else:
                # if this user has already rated this artist
                flash("you have already rated this artist")
                return render_template('artist.html', artist=artist, beefs=beefs, page_title=artist[0]['name'])
        else:
            flash('you need to be logged in to rate artists')
            return render_template('artist.html', artist=artist, beefs=beefs, page_title=artist[0]['name'])

# Page to contribute new information to the site        
@app.route('/contribute/')
def contribute_home():
    type = request.args.get('type')
    if type:
        return redirect(url_for('contribution_type', type=type))
    return render_template('contribute.html') 

# Takes the user to a page to contribute the correct type, either
# to add a new artist, album, or beef.
@app.route('/contribution/<type>', methods=['GET', 'POST'])
def contribution_type(type):
    conn = dbi.connect()
    genres = music.get_genres(conn)
    artists = music.get_artists(conn)

    # -------------------------------
    # 1. MUSIC (album submission)
    # -------------------------------
    if type == 'music':
        if request.method == 'GET':
            return render_template('album_form.html', artists=artists)

        # POST
        user_id = session.get('user_id')
        if not user_id:
            flash("You must be logged in to submit an album.")
            return redirect(url_for('login'))

        artist = request.form.get('artist')
        title = request.form.get('album')
        release = request.form.get('release')

        # Validation
        if not artist:
            flash("Please choose an artist.")
            return render_template('album_form.html', artists=artists)

        if not title:
            flash("Please add an album title.")
            return render_template('album_form.html', artists=artists)

        if not release:
            flash("Please add a release date.")
            return render_template('album_form.html', artists=artists)

        # Try DB insert
        try:
            music.create_album(conn, title, release, artist)
            flash(f"Album '{title}' submitted successfully and is pending approval!")
            return redirect(url_for('contribution_type', type='music'))
        except IntegrityError:
            flash("That album already exists.")
            return render_template('album_form.html', artists=artists)

    # -------------------------------
    # 2. ARTIST (add artist)
    # -------------------------------
    elif type == 'artist':
        if request.method == 'GET':
            return render_template('add-artist.html', artists=artists, genres=genres)

        # POST
        user_id = session.get('user_id')
        if not user_id:
            flash("You must be logged in to submit an artist.")
            return redirect(url_for('login'))

        name = request.form.get('name')
        genre = request.form.get('genre')
        rating = request.form.get('rating', 0)
        

        if not name or not genre:
            flash("Please fill in all required fields.")
            return render_template('add-artist.html', artists=artists, genres=genres)

        # Validate rating
        try:
            rating = int(rating)
        except ValueError:
            flash("Rating must be a number.")
            return render_template('add-artist.html', artists=artists, genres=genres)

        try:
            music.add_artist(conn, name, genre, rating)
            flash(f"Artist '{name}' submitted successfully and is pending approval!")
            return redirect(url_for('contribution_type', type='artist'))
        except IntegrityError:
            flash("That artist already exists!")
            return render_template('add-artist.html', artists=artists, genres=genres)

    # -------------------------------
    # 3. BEEF (add beef)
    # -------------------------------
    elif type == 'beef':
        if request.method == 'GET':
            return render_template('beef_form.html', artists=artists)

        # POST
        user_id = session.get('user_id')
        if not user_id:
            flash("You must be logged in to submit beef.")
            return redirect(url_for('login'))

        artist1 = request.form.get('artist1')
        artist2 = request.form.get('artist2')
        context = request.form.get('reason', "")
        side = request.form.get('side')

        # Validation
        if artist1 == artist2:
            flash("An artist cannot beef with themselves!")
            return render_template('beef_form.html', artists=artists)

        if artist1 == 'none' or artist2 == 'none':
            flash("Please choose two valid artists.")
            return render_template('beef_form.html', artists=artists)

        # Who user sides with
        countArtist1 = 1 if side == "artist1" else 0
        countArtist2 = 1 if side == "artist2" else 0

        # Fetch names for flash message
        artist_name1 = music.get_artist(conn, artist1)[0]['name']
        artist_name2 = music.get_artist(conn, artist2)[0]['name']

        try:
            music.create_beef(conn, artist1, artist2, context, countArtist1, countArtist2)
            flash(f"Beef between {artist_name1} and {artist_name2} submitted successfully and is pending approval!")
            return redirect(url_for('contribution_type', type='beef'))
        except IntegrityError:
            flash("That beef already exists!")
            return render_template('beef_form.html', artists=artists)

    # -------------------------------
    # Invalid Type
    # -------------------------------
    else:
        flash("Invalid contribution type.")
        return redirect(url_for('home'))



#forums home page to decide where the user wants to navigate
@app.route('/forums/')
def forums_home():
    if request.method == 'POST':
        type = request.form.get('type')
        if type:
            return redirect(url_for('forums_type', type=type))
    return render_template('forums.html') 

# Forum pages, where the user is taken to the music, explore, or 
# beef forum.
# Music forum is for artist and album discussions, explore is for 
# music recommendations, and beef is for discussing beefs.
@app.route('/forums/<type>', methods=['GET', 'POST'])
def forums_type(type):
    conn = dbi.connect()

    if type not in ['music', 'explore', 'beef']:
        forums = music.load_forums(conn, type)
        return render_template('forums.html', type=type, forums=forums)

    if request.method == 'POST':
        title = request.form.get('title')
        user_id = session.get('user_id')
        if title:
            music.insert_to_forums(conn, type, title, user_id)
        else:
            flash("Forum title required!")

    forums = music.load_forums(conn, type)
    template_map = {
        'music': 'forums-music.html',
        'explore': 'forums-explore.html',
        'beef': 'forum-beef.html'
    }
    return render_template(template_map[type], type=type, forums=forums)

# brings the user to the correct formum they want to discuss on
@app.route('/forums/<type>', methods=['GET', 'POST'])
def forums_type(type):
    conn = dbi.connect()
    if type == 'music':
        if request.method == 'POST': 
            # want to select from the forums
            # or make a new forum
            if request.method == 'POST':
                title = request.form.get('title')
                user_id = session.get('user_id')
                if title:
                    music.insert_to_forums(conn, type, title, user_id)
                else:
                    flash("Forum title required!")
            forums = music.load_forums(conn, type)
            return render_template('forums-music.html',type=type, forums = forums)
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
            title = request.form.get('title')
            user_id = session.get('user_id')
            if title:
                music.insert_to_forums(conn, type, title, user_id)
            else:
                flash("Forum title required!")
        forums = music.load_forums(conn, type)
        return render_template('forum-beef.html',type=type, forums=forums)
    else:
        # default behavior
        forums = music.load_forums(conn, type)
        return render_template('forums.html', type=type, forums=forums)


# allows users to view the specific forum they are interested in or 
# add their own forum
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
    return render_template('view-forum.html', forum=forum, posts=posts, page_title='Forum')

@app.route('/beef/<int:bid>')
def beef_page(bid):
    conn = dbi.connect()
    beef = music.get_beef(conn, bid)

    if not beef:
        flash("Beef not found or not approved!")
        return redirect(url_for('index'))

    artist1 = music.get_artist_one(conn, beef['artist1'])
    artist2 = music.get_artist_one(conn, beef['artist2'])

    return render_template('beef_page.html', beef=beef, artist1=artist1, artist2=artist2, page_title='Beef')



# Displays the album, allows users to rate the album
@app.route('/album/<int:aid>')
def album_page(aid):
    conn = dbi.connect()
    album = music.get_album(conn, aid)

    if not album:
        flash("Album not found!")
        return redirect(url_for('index'))

    artist = music.get_artist_one(conn, album['artistID'])
    return render_template('album_page.html',album=album, artist=artist, page_title=album['title'])
    
    


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