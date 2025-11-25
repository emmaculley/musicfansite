"""
File where we put any queries we're using

Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 8th November 2025
"""


import cs304dbi as dbi


# will give back artist info for their page
def get_artist(conn, id):
    curs = dbi.dict_cursor(conn)
    curs.execute('select name, genre, rating, artistID from artist where artistID=%s', [id])
    artist = curs.fetchall()
    return artist

#will give back one artist's info for their page
def get_artist_one(conn, id):
    curs = dbi.dict_cursor(conn)
    curs.execute('select name, genre, rating, artistID from artist where artistID=%s', [id])
    artist = curs.fetchone()
    return artist

# will return the beef between 2 artists
def get_beef(conn, id):
    curs = dbi.dict_cursor(conn)
    curs.execute('select name from artist where artistID=(select artist1 from beef where artist2=%s) or artistID=(select artist2 from beef where artist1=%s)', [id, id])
    beefs1 = curs.fetchone()
    return beefs1

# inserts a users rating into the db 
def insert_rating(conn, form_data, artistID):
    # puts a rating into the ratings table
    curs = dbi.dict_cursor(conn)
    curs.execute('insert into ratings values (%s, %s, %s)', [artistID, int(form_data['rating']), int(form_data['userID'])])
    conn.commit()

#updates the rating of the artist
def update_artist_rating(conn, artistID):
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

# returns a random list of 5 artists that fit into the given categories 
def discover_artists(conn, genre, num_rating):
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
    return curs.fetchall()

# returns a random list of 5 albums that fit into the given categories 
def discover_albums(conn, genre, num_rating):
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
    return curs.fetchall()

# returns a random list of 5 beefs that fit into the given categories 
def discover_beefs(conn, artist, genre):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select b.*, ar.genre from beef b
        join artist ar ON b.artist1 = ar.artistID
        where b.approved = "approved" AND b.artist1 = %s
            AND ar.genre = %s
        order by rand() 
        limit 5''', [artist, genre])
    return curs.fetchall()


#finds user in the db using their email
def get_user_by_email(conn, email):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from user where user_email = %s''', [email])
    return curs.fetchone() 

#creates a user who is entering the website for the first time
def create_user(conn, email, fname, lname, password):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into user (user_email, fname, lname, password) values (%s, %s, %s, %s)''',
        [email, fname, lname, password])
    conn.commit()
    return get_user_by_email(conn, email)

#creates beef between 2 given artists in the db
def create_beef(conn, artist1, artist2, context, countArtist1, countArtist2):
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''INSERT INTO beef (artist1, artist2, context, countArtist1, countArtist2)
           VALUES (%s, %s, %s, %s, %s)''',
        [artist1, artist2, context, countArtist1, countArtist2]
    )
    conn.commit()
    return curs.lastrowid

    ###if the artists are not already defined, need to create an artist (name, autogenerates an ID, and a genre)

#returns the beef given the beef id
def get_beef(conn, bid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM beef WHERE bid = %s''', [bid])
    return curs.fetchone()

<<<<<<< HEAD
=======
# adds an album in the db -- linked to the artist
def create_album(conn, title, release, artistID):
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''INSERT INTO album (title, `release`, artistID)
           VALUES (%s, %s, %s)''',
        [title, release, artistID]
    )
    conn.commit()
    return curs.lastrowid

#returns the album given the album id
def get_album(conn, albumID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT * FROM album WHERE albumID = %s''', [albumID])
    return curs.fetchone()

# returns a users password given the users email
>>>>>>> a92819123a378a7d2a23376e255d51a57f6d113c
def get_password(conn, email):
    curs = dbi.dict_cursor(conn)
    user = get_user_by_email(conn, email)
    if user:
        user_password = user['password']
        return user_password
    else:
        flash('You are not a user')

# inserts a new forum into the db
def insert_to_forums(conn, type, title, user_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into forum (title, userID, created_at, type)
        values (%s, %s, now(), %s)''', (title, user_id, type))
    return conn.commit()

# inserts a post into the db
def insert_post(conn, forum_id, user_id, content):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into post (forum_id, userID, created_at, content) 
        values (%s, %s, now(), %s)''', (forum_id, user_id, content))
    return conn.commit()

# returns all of the forums of a specific type
def load_forums(conn, type):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select forum_id, title from forum where type = %s order by created_at desc''', (type,))
    return curs.fetchall()

#returns one forum given the forum id
def get_forum(conn, forum_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from forum where forum_id = %s''', (forum_id))
    return curs.fetchone()

#returns all of the posts in a forum given the forum id
def get_posts(conn, forum_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from post where forum_id = %s order by created_at asc''', (forum_id))
    return curs.fetchall()

# returns all of the genres in the db
def get_genres(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute("select distinct genre from artist")
    return [row['genre'] for row in curs.fetchall()]

#returns all of the approved artists in the db
def get_artists(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''
        SELECT artistID, name
        FROM artist
        WHERE approvalStatus = 'approved'
        '''
    )
    return curs.fetchall()

# returns all of the approved albums in the db
def get_albums(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''
        SELECT albumID, title
        FROM album
        WHERE approved = 'approved'
        '''
    )
    return curs.fetchall()

