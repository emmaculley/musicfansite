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
