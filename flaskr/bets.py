from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.auth import get_db
import requests
import datetime

bp = Blueprint('bets', __name__)

def get_inseason_sports():
    #will query api for the in season sports and returns the keys of these sports
    api = current_app.config['API']
    apikey = current_app.config['APIKEY']
    query_params = {'apiKey': apikey, 'all' :'false'}
    json = requests.get(api, params = query_params).json()
    keys = []
    for sport in json:
        keys.append(sport['key'])
    return keys

def uploadMLodds(sport_key, api_endpoint,  apikey):
    json = requests.get(api_endpoint+sport_key+'/odds/', params = {'apiKey':apikey,'regions':'us','markets':'h2h'}).json()
    get_db()
    for game in json:
        game_id = game['id']
        home_team = game['home_team']
        away_team = game['away_team']
        start_time = datetime.datetime.fromisoformat(game['commence_time'][:-1]+'+00:00') #utc start_time 
        bookies = game['bookmakers']
        mybooks = current_app.config['MY_BOOKS'].split(',')
        for book in bookies:
            book_name = book['title']
            if book_name not in mybooks:
                    continue
            outcomes = book['markets'][0]['outcomes']
            for outcome in outcomes:
                cur_team = outcome['name']
                cur_price = outcome['price']
                if cur_team == home_team:
                    ht_price = cur_price
                if cur_team == away_team:
                    at_price = cur_price
                
            utc_now = datetime.datetime.now(datetime.timezone.utc)
            if utc_now < start_time:
                ls_commencetime =  game['commence_time'].split('T')
                start_time_str = ls_commencetime[0] + ' ' + ls_commencetime[1][:-1]
                utc_now_str = utc_now.strftime('%Y-%m-%d %H:%M:%S')
                g.cursor.execute('INSERT into moneyline VALUES (\'{}\',\'{}\',\'{}\',{},\'{}\',{},\'{}\',\'{}\',\'{}\')'.format(game_id,sport_key,home_team,ht_price,away_team, at_price, book_name, start_time_str, utc_now_str))

def uploadSpreads(sport_key, api_endpoint, apikey):
    json = requests.get(api_endpoint+sport_key+'/odds/', params = {'apiKey':apikey,'regions':'us','markets':'spreads'}).json()
    for game in json:
        id = game['id']
        start_time = datetime.datetime.fromisoformat(game['commence_time'][:-1]+'+00:00')
        ht = game['home_team']
        at = game['away_team']
        mybooks = current_app.config['MY_BOOKS']
        get_db()
        for bookie in game['bookmakers']:
            book = bookie['title']
            if book not in mybooks:
                continue
            outcomes = bookie['markets'][0]['outcomes']
            for outcome in outcomes:
                if outcome['name']==at:
                    away_spread = outcome['point']
                    away_price = outcome['price']
                elif outcome['name']==ht:
                    home_spread = outcome['point']
                    home_price  = outcome['price']
            utc_now = datetime.datetime.now(datetime.timezone.utc)
            if utc_now < start_time:
                ls_commencetime =  game['commence_time'].split('T')
                start_time_str = ls_commencetime[0] + ' ' + ls_commencetime[1][:-1]
                utc_now_str = utc_now.strftime('%Y-%m-%d %H:%M:%S')
                g.cursor.execute('INSERT into spreads VALUES (\'{}\',\'{}\',\'{}\',{},{},\'{}\',{},{},\'{}\',\'{}\',\'{}\')'.format(id,sport_key,ht,home_spread,home_price,at,away_spread,away_price,book, start_time_str, utc_now_str)) 


@bp.route('/', methods = ('GET', 'POST'))
def index():
    if request.method == 'GET':
        return render_template('home.html')
    

@bp.route('/get_spreads', methods=('GET', 'POST'))
@bp.route('/get_spreads/<sport>', methods=('GET', 'POST'))
@login_required
def get_spreads(sport=None):
    if sport:
        #not none, so display moneylines for the sports
        get_db()
        g.cursor.execute('SELECT * FROM spreads WHERE sport_key = \'{}\' and Start_Time > \'{}\''.format(sport,datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))
        rows = g.cursor.fetchall()
        return render_template('bets/display_sp.html', data=rows)

    else:
        #sport is none
        if request.method == 'POST':
            sportkey = request.form['sportkey']
            in_seasons_keys = get_inseason_sports()

            error = None

            if not sportkey:
                error = 'Sport key is required.'
            if sportkey not in in_seasons_keys:
                error = 'invalid  sportkey'
            if error is not None:
                flash(error)
            else:
                uploadSpreads(sportkey,current_app.config['API'],current_app.config['APIKEY'])
                return redirect(url_for('.get_spreads',sport=sportkey))

        return render_template('bets/submit_sport.html')

@bp.route('/get_moneylines', methods=('GET', 'POST'))
@bp.route('/get_moneylines/<sport>', methods=('GET', 'POST'))
@login_required
def get_ml(sport=None):
    if sport:
        #not none, so display moneylines for the sports
        get_db()
        g.cursor.execute('SELECT * FROM moneyline WHERE sport_key = \'{}\' and Start_Time > \'{}\''.format(sport,datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))
        rows = g.cursor.fetchall()
        return render_template('bets/display_ml.html', data=rows)

    else:
        #sport is none
        if request.method == 'POST':
            sportkey = request.form['sportkey']
            in_seasons_keys = get_inseason_sports()

            error = None

            if not sportkey:
                error = 'Sport key is required.'
            if sportkey not in in_seasons_keys:
                error = 'invalid  sportkey'

            if error is not None:
                flash(error)
            else:
                uploadMLodds(sportkey,current_app.config['API'],current_app.config['APIKEY'])
                return redirect(url_for('.get_ml',sport=sportkey))

        return render_template('bets/submit_sport.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))