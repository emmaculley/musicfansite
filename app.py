"""
Music Fansite
Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 8th December 2025
"""

from flask import (Flask, render_template, url_for, request,
                   redirect, session, flash, send_from_directory)
from werkzeug.utils import secure_filename

app = Flask(__name__)

import sys, os
import secrets
import cs304dbi as dbi
import music
import bcrypt
from pymysql import IntegrityError

# for flashing
app.secret_key = secrets.token_hex()

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'artists')
app.config['UPLOADS'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

print(dbi.conf('musicfan_db'))
conn = dbi.connect()
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
    return render_template('discover.html', page_title='Discover') 

# brings the user to the correct form to discover what they're looking
# for (artists, albums, or beefs)
@app.route('/discover/<kind>', methods=['GET', 'POST'])
def discover_kind(kind):
    conn = dbi.connect()
    if kind == 'artist':
        if request.method == 'POST':
            genre = request.form.get('genre')
            num_rating = request.form.get('num_rating')

            if not genre:
                flash("Please make a selection for genre.")
                return redirect(url_for('discover_kind', kind='artist'))

            return redirect(url_for('discover_artist_results', genre=genre, num_rating=num_rating))

        genres = music.get_genres(conn)
        return render_template('discover-artist.html', genres=genres, page_title='Discover Artists')
    elif kind == 'album':
        if request.method == 'POST':
            genre = request.form.get('genre')
            num_rating = request.form.get('num_rating')

            if not genre:
                flash("Please make a selection for genre.")
                return redirect(url_for('discover_kind', kind='album'))

            return redirect(url_for('discover_album_results', genre=genre, num_rating=num_rating))

        genres = music.get_genres(conn)
        return render_template('discover-album.html', genres=genres, page_title='Discover Albums')
    elif kind == 'beef':
        if request.method == 'POST':
            artist = request.form.get('artist')
            if not artist:
                flash("Please select an artist.")
                return redirect(url_for('discover_kind', kind='beef'))

            return redirect(url_for('discover_beef_results', artist=artist))

        genres = music.get_genres(conn)
        artists = music.get_artists(conn)
        return render_template('discover-beef.html', genres=genres, artists=artists, page_title='Discover Beefs')


@app.route('/discover/artist/results')
def discover_artist_results():
    genre = request.args.get('genre')
    num_rating = request.args.get('num_rating')
    conn = dbi.connect()
    artists = music.discover_artists(conn, genre, num_rating)

    if not artists:
        flash("There are no artists in this category with this number of ratings.")
        return redirect(url_for('discover_kind', kind='artist'))

    return render_template('discover-artist-results.html', genre=genre, num_rating=num_rating, artists=artists, page_title='Artists to Discover')

@app.route('/discover/album/results')
def discover_album_results():
    genre = request.args.get('genre')
    num_rating = request.args.get('num_rating')
    conn = dbi.connect()
    albums = music.discover_albums(conn, genre, num_rating)

    if not albums:
        flash("There are no albums in this category with this number of rating")
        return redirect(url_for('discover_kind', kind='album'))

    return render_template('discover-album-results.html', genre=genre, num_rating=num_rating, albums=albums, page_title='Albums to Discover')


@app.route('/discover/beef/results')
def discover_beef_results():
    artist_id = request.args.get('artist')
    conn = dbi.connect()

    artistInfo = music.get_artist_one(conn, artist_id)
    if not artistInfo:
        flash("Artist not found.")
        return redirect(url_for('discover_kind', kind='beef'))

    artistName = artistInfo['name']
    beefs = music.discover_beefs(conn, artist_id)

    if not beefs:
        flash("This artist has no beefs.")
        return redirect(url_for('discover_kind', kind='beef'))

    for beef in beefs:
        artist1 = beef["artist1"]
        artist2 = beef["artist2"]
        beef['artist1Name'] = music.get_artist_one(conn, artist1)['name']
        beef['artist2Name'] = music.get_artist_one(conn, artist2)['name']

    return render_template('discover-beef-results.html', artist=artistName, beefs=beefs, page_title='Beefs to Discover')




# pages for individual artists
@app.route('/artist/<id>/', methods = ['GET', 'POST'])
def artist(id):
    conn = dbi.connect()
    artist = music.get_artist(conn, id)
    beefs = music.get_beef_names(conn, id) or [] 
    photo_filename = music.get_artist_photo(conn, id)
    for beef in beefs:
        artist1ID = artist[0]['artistID']
        artist2ID = beef['artistID']
        beefID = music.get_beef_id(conn, artist1ID, artist2ID)
        beef['beefID'] = beefID['bid']
    if request.method == 'POST':
        form_data = request.form
        if 'user_id' in session:
            user_id = session['user_id']
            artistID = artist[0]['artistID']
            potential_rating = music.check_ratings(conn, user_id, artistID)
            if potential_rating is None:
                music.insert_rating(conn, form_data, id, user_id)
                music.update_artist_rating(conn, id)
                artist = music.get_artist(conn, id)
                flash("Rating submitted successfully.")
            else:
                flash("You have already rated this artist")
        else:
            flash('You need to be logged in to rate artists')
    return render_template('artist.html', artist=artist, beefs=beefs, photo=photo_filename, page_title=artist[0]['name'])


        


# Page to contribute new information to the site        
@app.route('/contribute/')
def contribute_home():
    type = request.args.get('type')
    if type:
        return redirect(url_for('contribution_type', type=type))
    return render_template('contribute.html', page_title='Contribute') 

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
            return render_template('album_form.html', artists=artists, page_title='Album Form')

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
            return render_template('album_form.html', artists=artists, page_title='Album Form')

        if not title:
            flash("Please add an album title.")
            return render_template('album_form.html', artists=artists, page_title='Album Form')

        if not release:
            flash("Please add a release date.")
            return render_template('album_form.html', artists=artists, page_title='Album Form')

        # Try DB insert
        try:
            music.create_album(conn, title, release, artist)
            flash(f"Album '{title}' submitted successfully and is pending approval!")
            return redirect(url_for('contribution_type', type='music'))
        except IntegrityError:
            flash("That album already exists.")
            return render_template('album_form.html', artists=artists, page_title='Album Form')

    # -------------------------------
    # 2. ARTIST (add artist)
    # -------------------------------
    elif type == 'artist':
        if request.method == 'GET':
            return render_template('add-artist.html', artists=artists, genres=genres, page_title='Add Artist')

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
            return render_template('add-artist.html', artists=artists, genres=genres, page_title='Add Artist')

        # Validate rating
        try:
            rating = int(rating)
        except ValueError:
            flash("Rating must be a number.")
            return render_template('add-artist.html', artists=artists, genres=genres, page_title='Add Artist')

        try:
            music.add_artist(conn, name, genre, rating)
            flash(f"Artist '{name}' submitted successfully and is pending approval!")
            return redirect(url_for('contribution_type', type='artist'))
        except IntegrityError:
            flash("That artist already exists!")
            return render_template('add-artist.html', artists=artists, genres=genres, page_title='Add Artist')

    # -------------------------------
    # 3. BEEF (add beef)
    # -------------------------------
    elif type == 'beef':
        if request.method == 'GET':
            return render_template('beef_form.html', artists=artists, page_title='Beef Form')

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
            return render_template('beef_form.html', artists=artists, page_title='Beef Form')

        if artist1 == 'none' or artist2 == 'none':
            flash("Please choose two valid artists.")
            return render_template('beef_form.html', artists=artists, page_title='Beef Form')

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
            return render_template('beef_form.html', artists=artists, page_title='Beef Form')

    # -------------------------------
    # Invalid Type
    # -------------------------------
    else:
        flash("Invalid contribution type.")
        return redirect(url_for('home'))



#forums home page to decide where the user wants to navigate
@app.route('/forums/', methods=['GET', 'POST'])
def forums_home():
    if request.method == 'POST':
        type = request.form.get('type')
        if type:
            return redirect(url_for('forums_type', type=type))
    return render_template('forums.html', page_title = "forums") 


# Forum pages, where the user is taken to the music, explore, or 
# beef forum.
# Music forum is for artist and album discussions, explore is for 
# music recommendations, and beef is for discussing beefs.
# brings the user to the correct formum they want to discuss on
@app.route('/forums/<type>', methods=['GET', 'POST'])
def forums_type(type):
    conn = dbi.connect()

    # Invalid type
    if type not in ['music', 'explore', 'beef']:
        flash("Invalid forum type!")
        return redirect(url_for('forums_home'))

    # Handle POST only for music/explore forums
    if request.method == 'POST' and type != 'beef':
        title = request.form.get('title')
        user_id = session.get('user_id')
        if title:
            music.insert_to_forums(conn, type, title, user_id)
        else:
            flash("Forum title required!")

    # SPECIAL CASE: beef forums → load beefs, not forums
    if type == 'beef':
        beefs = music.load_all_beefs(conn)   # YOU CREATE THIS FUNCTION
        return render_template('forum-beef.html', beefs=beefs, page_title = "Beef Forum")

    # Default: load normal forums
    forums = music.load_forums(conn, type)

    template_map = {
        'music': 'forums-music.html',
        'explore': 'forums-explore.html',
    }

    return render_template(template_map[type], type=type, forums=forums, page_title = "forum type")


# Lets users vote for an artist in a beef. If a user has already 
# placed a vote in the beef, they can update their vote to support 
# the other artist.
@app.route('/vote/<int:bid>/<int:artist_id>', methods=['POST'])
def vote(bid, artist_id):
    # must be logged in
    if 'user_id' not in session:
        flash("You must be logged in to vote.")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Check if they already voted for this beef

    existing = music.voted(conn,user_id,bid)

    if existing:
        # update vote
        music.update_vote(conn, artist_id, user_id, bid)
    else:
        # new vote
        music.new_vote(conn, user_id, bid, artist_id)

    flash("Your vote has been updated!")
    return redirect(url_for('beef_page', bid=bid))



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


# Displays the beef pages. 
@app.route('/beef/<int:bid>')
def beef_page(bid):
    conn = dbi.connect()
    beef = music.get_beef(conn, bid)

    if not beef:
        flash("Beef not found or not approved!")
        return redirect(url_for('forums_type', type = 'beef'))

    artist1 = music.get_artist_one(conn, beef['artist1'])
    artist2 = music.get_artist_one(conn, beef['artist2'])
    
    # load vote totals
    total_votes = music.total_votes(conn, bid, beef['artist1'], beef['artist2'])
    return render_template('beef_page.html',
                           beef=beef, 
                           artist1=artist1, 
                           artist2=artist2, 
                           counts=total_votes,
                           page_title='Beef')


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
    
# allows users to search for albums and artists directly
@app.route('/search')
def search_page():
    conn = dbi.connect()
    term = request.args.get('term')
    artists = []
    albums = []
    if term:
        artists = music.search_artists(conn, term)
        albums = music.search_albums(conn, term)
    return render_template('search.html',term=term,artists=artists,albums=albums,page_title="Search")

# allows users to upload a photo of the artist for their artist page
@app.route('/upload_artist_photo/', methods=['GET', 'POST'])
def upload_artist_photo():
    if 'user_id' not in session:
        flash("You must be logged in to upload a photo.")
        return redirect(url_for('login'))
    conn = dbi.connect()
    if request.method == 'GET':
        artists = music.get_artists(conn)
        return render_template(
            'upload_artist_photo.html',
            artists=artists,
            src='',
            artistID=''
        )
    else:
        try:
            artistID = int(request.form['artistID'])
            f = request.files['photo']
            user_filename = f.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename(f'artist_{artistID}.{ext}')
            pathname = os.path.join(app.config['UPLOADS'], filename)
            f.save(pathname)
            music.save_artist_photo(conn, artistID, filename)
            flash('Artist photo upload successful')
            return render_template(
                'upload_artist_photo.html',
                artists=music.get_artists(conn),
                src=url_for('artist_pic', artistID=artistID),
                artistID=artistID
            )
        except Exception as err:
            flash(f'Upload failed: {err}')
            return render_template(
                'upload_artist_photo.html',
                artists=music.get_artists(conn),
                src='',
                artistID='')

# gets the artist photo 
@app.route('/artist_pic/<int:artistID>/')
def artist_pic(artistID):
    conn = dbi.connect()
    filename = music.get_artist_photo(conn, artistID)
    if not filename:
        return url_for('static', filename='uploads/artists/placeholder.png')
    return send_from_directory(app.config['UPLOADS'], filename)



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