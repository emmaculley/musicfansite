"""
File where we put any queries we're using

Authors: Emma Culley, Dana Hammouri, Megan O'Leary, Ashley Yang
Last updated: 5th November 2025
"""


import cs304dbi as dbi


# will give back artist info for their page
def get_artist(conn, id):
    curs = dbi.dict_cursor(conn)
    curs.execute('select name, genre, rating from artist where artistID=%s', [id])
    name, genre, rating = curs.fetchall()
    return name, genre, rating