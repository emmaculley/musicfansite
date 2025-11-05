'''
Music Fansite Draft version
Ashley, Dana, Emma, and Megan
'''
from flask import (Flask, render_template, request)

app = Flask(__name__)


@app.route('/discover/')
def discover():
    '''
    Returns the rendered page for the type inputted to the discover form.

    Args:
        None
    Return:
        String of the rendered template -> str
    '''
    query_type = request.args.get('kind')
    conn = dbi.connect()

    if query_type == 'artist':
        return render_template('discover-artist.html')

    if query_type == 'album':
        return render_template('discover-album.html')   

    if query_type == 'beef':
        return render_template('discover-beef.html')   