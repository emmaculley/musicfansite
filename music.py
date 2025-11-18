"""
File where we put any queries we're using

Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 8th November 2025
"""


import cs304dbi as dbi

# will give back artist info for their page
def get_artist(conn, id):
    curs = dbi.dict_cursor(conn)
    curs.execute('select name, genre, rating from artist where artistID=%s', [id])
    name, genre, rating = curs.fetchall()
    return name, genre, rating

#will return artist ID from t

# returns a random list of 5 artists that fit into the given categories 
def discover_artists(conn, genre, num_rating):
    curs = dbi.dict_cursor(conn)
    query = '''select a.*, count(r.userID) as num_ratings from artist a
        join ratings r on a.artistID = r.artistID
        where a.approvalStatus = "approved" AND a.genre = %s
        group by a.artistID'''
    if num_rating == "100":
        query += 'having num_ratings >= 100'
    elif num_rating == "75":
        query += 'having num_ratings >= 75 AND num_ratings < 100'
    elif num_rating == "50":
        query += 'having num_ratings >= 50 AND num_ratings < 75'
    elif num_rating == "25":
        query += 'having num_ratings >= 25 AND num_ratings < 50'
    elif num_rating == "0":
        query += 'having num_ratings >= 0 AND num_ratings < 25'
    query += ' order by rand() limit 5'
    curs.execute(query, [genre])
    return curs.fetchall()

# returns a random list of 5 albums that fit into the given categories 
def discover_albums(conn, genre, num_rating):
    curs = dbi.dict_cursor(conn)
    query = '''select a.*, count(r.userID) as num_ratings from album a
        join ratings r on a.artistID = r.artistID
        where a.approvalStatus = "approved" AND a.genre = %s
        group by a.artistID''',
    if num_rating == "100":
        query += 'having num_ratings >= 100'
    elif num_rating == "75":
        query += 'having num_ratings >= 75 AND num_ratings < 100'
    elif num_rating == "50":
        query += 'having num_ratings >= 50 AND num_ratings < 75'
    elif num_rating == "25":
        query += 'having num_ratings >= 25 AND num_ratings < 50'
    elif num_rating == "0":
        query += 'having num_ratings >= 0 AND num_ratings < 25'
    query += ' order by rand() limit 5'
    curs.execute(query, [genre])
    return curs.fetchall()

# returns a random list of 5 beefs that fit into the given categories 
def discover_beefs(conn, artist, genre):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from beef where approved = "approved" 
     AND artist1 = %s AND genre = %s order by rand() limit 5''',[artist, genre])
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
    get_user_by_email(conn, email)
    return curs.fetchone()


def create_beef(conn, artist1, artist2, countArtist1, countArtist2, context):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into beef (artist1, artist2, countArtist1, countArtist2, context) values (%s, %s, %s,%s, %s, %s)''',
        [artist1, artist2, countArtist1, countArtist2, context])
    conn.commit()
    return cur.lastrowid

    ###if the artists are not already defined, need to create an artist (name, autogenerates an ID, and a genre)



def get_password(conn, email):
    curs = dbi.dict_cursor(conn)
    get_user_by_email(conn, email)
    user = curs.fetchone()
    if user:
        user_password = user['password']
        return user_password
    else:
        flash('You are not a user')

def insert_to_forums(conn, type, title, user_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into forum (title, userID, created_at, type)
        values (%s, %s, now(), %s)''', (title, user_id, kind))
    return conn.commit()

def load_forums(conn, type):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select forum_id, title from forum where type = %s order by created_at desc''', (type,))
    return curs.fetchall()

def get_forum(conn, forum_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from forum where forum_id = %s''', (forum_id))
    return curs.fetchone()

def get_posts(conn, forum_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from post where forum_id = %s order by created_at asc''', (forum_id))
    return curs.fetchall()

def get_genres(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute("select distinct genre from artist")
    return [row['genre'] for row in curs.fetchall()]

