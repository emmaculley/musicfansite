"""
File where we put any queries we're using

Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 8th November 2025
"""


import cs304dbi as dbi

def load_all_beefs(conn):
    '''
    Returns all approved beefs from the beef table

    Args:
        None
    Return:
        All approved beefs
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute("""
        SELECT 
            b.bid,
            b.artist1,
            b.artist2,
            COALESCE(a1.name, '') AS artist1_name,
            COALESCE(a2.name, '') AS artist2_name
        FROM beef b
        LEFT JOIN artist a1 ON b.artist1 = a1.artistID
        LEFT JOIN artist a2 ON b.artist2 = a2.artistID
        WHERE b.approved = 'approved'
    """)
    return curs.fetchall()

def voted(conn, user_id, bid):
    '''
    Checks if user has already voted in this beef

    Args:
        user_id -> int
        bid -> int
    Return:
        Returns vote if the user has already voted, None otherwise
    '''
    curs = dbi.dict_cursor(conn)

    # Check if they already voted for this beef
    curs.execute("""
        SELECT voted_for FROM beef_votes
        WHERE user_id = %s AND bid = %s
    """, [user_id, bid])

    return curs.fetchone()

def update_vote(conn, artist_id, user_id, bid):
    '''
    Updates vote in the beef table

    Args:
        artist_id -> int
        user_id -> int
        bid -> int
    Return:
        None
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute("""
            UPDATE beef_votes
            SET voted_for = %s
            WHERE user_id = %s AND bid = %s
        """, [artist_id, user_id, bid])
    conn.commit()

def new_vote(conn, user_id, bid, artist_id):
    '''
    Inserts a new vote into the beef table

    Args:
        user_id -> int
        bid -> int
        artist_id -> int
    Return:
        None
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute("""
            INSERT INTO beef_votes (user_id, bid, voted_for)
            VALUES (%s, %s, %s)
        """, [user_id, bid, artist_id])
    conn.commit()

def total_votes(conn, bid, artist1_id, artist2_id):
    '''
    Returns the total votes for both artists in a beef

    Args:
        bid -> int
        artist1_id -> int
        artist_id -> int
    Return:
        None
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute("""
        SELECT
            SUM(voted_for = %s) AS artist1_votes,
            SUM(voted_for = %s) AS artist2_votes
        FROM beef_votes
        WHERE bid = %s
    """, [artist1_id, artist2_id, bid])
    counts = curs.fetchone()
    # Ensure counts are integers even if there are no votes yet
    return {
        'artist1_votes': counts['artist1_votes'] or 0,
        'artist2_votes': counts['artist2_votes'] or 0
    }

def add_artist(conn, name, genre, rating):
    '''
    Inserts an artist into the artist table in the database.

    Args:
        name -> str
        genre -> str
        rating -> str
    Return:
        None
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into artist (name, genre, rating, approvalStatus)
        values (%s, %s, %s, 'pending')''', (name, genre,rating))
    conn.commit()

def add_album(conn, title, release, artistID):
    '''
    Inserts an album into the album table in the database.

    Args:
        title -> str
        release -> str
        artistID -> int
    Return:
        None
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into album (title, `release`, artistID, approved)
        values (%s, %s, %s , 'pending')''', (title, release, artistID))
    conn.commit()
    

def get_artist(conn, id):
    '''
    Returns all artists given their artistID

    Args:
        id -> int
    Return:
        The artist's information given their artistID
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('select name, genre, rating, artistID from artist where artistID=%s', [id])
    artist = curs.fetchall()
    return artist


def get_artist_one(conn, id):
    '''
    Returns an artists given their artistID

    Args:
        id -> int
    Return:
        The artist's information given their artistID
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('select name, genre, rating, artistID from artist where artistID=%s', [id])
    artist = curs.fetchone()
    return artist


def get_beef_names(conn, id):
    '''
    Returns all beefs given an artist has given their artistID

    Args:
        id -> int
    Return:
        The artist's beefs
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('select name, artistID from artist where artistID in (select artist1 from beef where artist2=%s) or artistID in (select artist2 from beef where artist1=%s)', [id, id])
    beefs = curs.fetchall()
    return beefs


def insert_rating(conn, form_data, artistID, userID):
    '''
    Inserts a users rating into the database

    Args:
        form_data -> str
        artistID -> int
        userID -> int
    Return:
        None
    '''
    # puts a rating into the ratings table
    curs = dbi.dict_cursor(conn)
    curs.execute('insert into ratings values (%s, %s, %s)', [artistID, int(form_data['rating']), userID])
    conn.commit()


def update_artist_rating(conn, artistID):
    '''
    Updates the artist's rating in the artist table

    Args:
        artistID -> int
    Return:
        None
    '''
    # updates the artist's rating in the artist table
    curs = dbi.dict_cursor(conn)
    curs.execute('select rating from ratings where artistID = %s', [artistID])
    ratings = curs.fetchall()
    totalRating = 0
    countRatings = 0
    # compute the artist's average rating:
    for rating in ratings:
        totalRating += rating["rating"]
        countRatings += 1
    avgRating = totalRating/countRatings
    curs.execute('update artist set rating =%s where artistID = %s', [avgRating, artistID])
    conn.commit()


def discover_artists(conn, genre, num_rating):
    '''
    Returns a random list of 5 artists that fit into the given categories
    OR all of the artists that fit the given criteria if less than 5 artists

    Args:
        genre -> str
        num_rating -> int
    Return:
        5 (or fewer) artists who fit the form criteria
    '''
    curs = dbi.dict_cursor(conn)
    query = '''select a.*, count(r.userID) as num_ratings from artist a
        left join ratings r on a.artistID = r.artistID
        where a.approvalStatus = "approved" AND a.genre = %s
        group by a.artistID'''
    if num_rating == "100":
        query += ' having num_ratings >= 100'
    elif num_rating == "75":
        query += ' having num_ratings >= 75 AND num_ratings < 100'
    elif num_rating == "50":
        query += ' having num_ratings >= 50 AND num_ratings < 75'
    elif num_rating == "25":
        query += ' having num_ratings >= 25 AND num_ratings < 50'
    elif num_rating == "0":
        query += ' having num_ratings >= 0 AND num_ratings < 25'
    query += ' order by rand() limit 5'
    curs.execute(query, [genre])
    artists = curs.fetchall()
    if not artists:
        return None
    return artists


def discover_albums(conn, genre, num_rating):
    '''
    Returns a random list of 5 albums that fit into the given categories
    OR all of the albums that fit the given criteria if less than 5 albums

    Args:
        genre -> str
        num_rating -> int
    Return:
        5 (or fewer) albums who fit the form criteria
    '''
    curs = dbi.dict_cursor(conn)
    query = '''SELECT a.*, COUNT(r.userID) AS num_ratings
        from album a left join artist ar using (artistID)
        left join ratings r using (artistID)
        where a.approved = 'approved' AND ar.genre = %s
        group by a.albumID'''
    if num_rating == "100":
        query += ' having num_ratings >= 100'
    elif num_rating == "75":
        query += ' having num_ratings >= 75 AND num_ratings < 100'
    elif num_rating == "50":
        query += ' having num_ratings >= 50 AND num_ratings < 75'
    elif num_rating == "25":
        query += ' having num_ratings >= 25 AND num_ratings < 50'
    elif num_rating == "0":
        query += ' having num_ratings >= 0 AND num_ratings < 25'
    query += ' order by rand() limit 5'
    curs.execute(query, [genre])
    albums = curs.fetchall()
    if not albums:
        return None
    return albums

 
def discover_beefs(conn, artist):
    '''
    Returns a random list of 5 beefs a given artist has
    OR all of the beefs that fit the given criteria if less than 5

    Args:
        artist -> str

    Return:
        5 (or fewer) beefs with a given artist
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select b.* from beef b
        where (b.artist1 = %s or b.artist2 = %s)
        and b.approved = 'approved'
        order by rand()
        limit 5''', [artist, artist])
    beefs = curs.fetchall()
    if not beefs:
        return None
    return beefs



def get_user_by_email(conn, email):
    '''
    Returns a user given their email

    Args:
        email -> str

    Return:
        The user's information from the user table given their email
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from user where user_email = %s''', [email])
    return curs.fetchone() 


def create_user(conn, email, fname, lname, password):
    '''
    Inserts a user who is using the website for the first time into the user table

    Args:
        email -> str
        fname -> str
        lname -> str
        password -> str
    Return:
        None
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into user (user_email, fname, lname, password) values (%s, %s, %s, %s)''',
        [email, fname, lname, password])
    conn.commit()
    return get_user_by_email(conn, email)


def create_beef(conn, artist1, artist2, context, countArtist1, countArtist2):
    '''
    Inserts a beef between 2 artists into the beef table

    Args:
        artist1 -> str
        artist2 -> str
        context -> str
        countArtist1 -> int
        countArtist2 -> int

    Return:
        beefID of the newly inserted beef 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''INSERT INTO beef (artist1, artist2, context, countArtist1, countArtist2)
           VALUES (%s, %s, %s, %s, %s)''',
        [artist1, artist2, context, countArtist1, countArtist2]
    )
    conn.commit()
    return curs.lastrowid

###if the artists are not already defined, need to create an artist (name, autogenerates an ID, and a genre)


def get_beef(conn, bid):
    '''
    Returns a beef given the beef id

    Args:
        bid -> str

    Return:
        The beefs's information from the beef table 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT *
        FROM beef
        WHERE bid = %s
          AND approved = 'approved'
    ''', [bid])
    return curs.fetchone()



def create_album(conn, title, release, artistID):
    '''
    Inserts a new album into the album table

    Args:
        title -> str
        release -> str
        artistID -> int

    Return:
        artistID of the newly inserted album 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''INSERT INTO album (title, `release`, artistID, approved)
           VALUES (%s, %s, %s, %s)''',
        [title, release, artistID, 'pending']
    )
    conn.commit()
    return curs.lastrowid


def get_album(conn, albumID):
    '''
    Returns an album given the albumID

    Args:
        albumID -> int

    Return:
        The album given the albumID
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM album WHERE albumID = %s''', [albumID])
    return curs.fetchone()


def get_password(conn, email):
    '''
    Returns the users password given their email

    Args:
        email -> str

    Return:
        The user's password
    '''
    curs = dbi.dict_cursor(conn)
    user = get_user_by_email(conn, email)
    if user:
        user_password = user['password']
        return user_password
    else:
        flash('You are not a user')


def insert_to_forums(conn, type, title, user_id):
    '''
    Inserts a new forum into the forum table

    Args:
        type -> str
        title -> str
        user_id -> int

    Return:
        None
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into forum (title, userID, created_at, type)
        values (%s, %s, now(), %s)''', (title, user_id, type))
    return conn.commit()


def insert_post(conn, forum_id, user_id, content):
    '''
    Inserts a new post into the post table for a given forum

    Args:
        forum_id -> int
        user_id -> int
        content -> str

    Return:
        None
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into post (forum_id, userID, created_at, content) 
        values (%s, %s, now(), %s)''', (forum_id, user_id, content))
    return conn.commit()


def load_forums(conn, type):
    '''
    Returns all of the forums of a specific type

    Args:
        type -> str

    Return:
        All the matching forums
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select forum_id, title from forum where type = %s order by created_at desc''', (type,))
    return curs.fetchall()


def get_forum(conn, forum_id):
    '''
    Returns one forum given its forumID

    Args:
        forum_id -> int

    Return:
        Corresponding forum to the forumID
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from forum where forum_id = %s''', (forum_id))
    return curs.fetchone()


def get_posts(conn, forum_id):
    '''
    Returns all of the posts in a forum given the forumID

    Args:
        forum_id -> str

    Return:
        All the posts from the given forum
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from post where forum_id = %s order by created_at asc''', (forum_id))
    return curs.fetchall()


def get_genres(conn):
    '''
    Returns all of the genres in the database

    Args:
        None

    Return:
        All the genres in the database
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute("select distinct genre from artist")
    return [row['genre'] for row in curs.fetchall()]


def get_artists(conn):
    '''
    Returns all of the approved artists in the database

    Args:
        None

    Return:
        All the approved artists in the database
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''
        SELECT artistID, name
        FROM artist
        WHERE approvalStatus = 'approved'
        ORDER BY name
        '''
    )
    return curs.fetchall()


def get_albums(conn):
    '''
    Returns all of the approved albums in the database

    Args:
        None 

    Return:
        All the approved albums in the database
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''
        SELECT albumID, title
        FROM album
        WHERE approved = 'approved'
        '''
    )
    return curs.fetchall()


def get_beef_id(conn, id1, id2):
    '''
    Returns a beef an artist has given an artistID

    Args:
        id -> int 

    Return:
        A beef an artist has had given their artistID
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('select bid from beef where (artist1=%s and artist2=%s) or (artist1=%s and artist2=%s)', [id1, id2, id2, id1])
    return curs.fetchone()


def check_ratings(conn, userID, artistID):
    '''
    Returns an artists rating from a user given their artistID and userID

    Args:
        userID -> int 
        artistID -> int

    Return:
        The artist's rating as given by the user
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('select userID from ratings where artistID=%s AND userID=%s', [artistID, userID])
    return curs.fetchone()


def search_artists(conn, term):
    '''
    Search for artists whose name matches the search.
    
    Args:
        term -> str 

    Returns:
        A list of dicts with artistID, name, genre, rating, approvalStatus.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT artistID, name, genre, rating, approvalStatus
        FROM artist
        WHERE name LIKE %s'''
    curs.execute(sql, ['%' + term + '%'])
    return curs.fetchall()


def search_albums(conn, term):
    '''
    Search for albums whose title matches the search.

    Args:
        term -> str 

    Returns:    
        Returns a list of dicts with albumID, title, release, artistID, approved.
    '''
    curs = dbi.dict_cursor(conn)
    sql = ''' SELECT albumID, title, `release`, artistID, approved
        FROM album
        WHERE title LIKE %s'''
    curs.execute(sql, ['%' + term + '%'])
    return curs.fetchall()




