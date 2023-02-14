from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.helper_funcs import get_db, get_inseason_sports, uploadMLodds, uploadSpreads, deleteML, deleteSpreads,uploadScores, reformatMLQueryResult, reformatSpreadsQueryResult, reformatBets
import datetime

bp = Blueprint('bets', __name__)


@bp.route('/home', methods = ('GET', 'POST'))
@login_required
def index():
    if request.method == 'GET':
        get_db()
        #this block deletes games from spreads and moneyline table which have already occurred
        deleteSpreads()  
        deleteML()
        #
        uploadScores()
        return render_template('home.html')
    elif request.method == 'POST':
        if request.form.get('button') == 'Spreads':
            return redirect(url_for('bets.get_spreads'))
        elif request.form.get('button') == 'Moneylines':
            return redirect(url_for('bets.get_ml'))
        else:
            return redirect(url_for('bets.index'))
    else:
        return redirect(url_for('bets.index'))

@bp.route('/get_spreads', methods=('GET', 'POST'))
@bp.route('/get_spreads/<sport>', methods=('GET', 'POST'))
@login_required
def get_spreads(sport=None):
    if sport:
        #not none, so display moneylines for the sports
        get_db()
        g.cursor.execute('SELECT * FROM spreads WHERE sport_key = \'{}\' and Start_Time > \'{}\''.format(sport,datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))
        rows = g.cursor.fetchall()
        return render_template('bets/display_sp2.html', data=reformatSpreadsQueryResult(rows))

    else:
        #sport is none
        if request.method == 'POST':
            sportkey = request.form.get('sportkeys')
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
        return render_template('bets/submit_sport.html', data=get_inseason_sports())

@bp.route('/get_moneylines', methods=('GET', 'POST'))
@bp.route('/get_moneylines/<sport>', methods=('GET', 'POST'))
@login_required
def get_ml(sport=None):
    if sport:
        #not none, so display moneylines for the sports
        get_db()
        g.cursor.execute('SELECT * FROM moneyline WHERE sport_key = \'{}\' and Start_Time > \'{}\''.format(sport,datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))
        rows = g.cursor.fetchall()
        return render_template('bets/display_ml2.html', data=reformatMLQueryResult(rows))

    else:
        #sport is none
        if request.method == 'POST':
            sportkey = request.form.get('sportkeys')
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

        return render_template('bets/submit_sport.html', data=get_inseason_sports())


@bp.route('/Balances', methods = ('GET', 'POST'))
@login_required
def add_get_Balance():
    get_db()
    if request.method == 'GET':
        g.cursor.execute('select book, amount from balance where username = \'{}\''.format(session.get('user_id')))
        return render_template('bets/balance.html',data={'mybooks': current_app.config['MY_BOOKS'], 'results':g.cursor.fetchall()})
    else:
        #post
        book = request.form.get('book')
        amount = float(request.form.get('amount'))
        g.cursor.execute('select * from balance where username = \'{}\' and book = \'{}\''.format(session.get('user_id'),book))
        rows = g.cursor.fetchall()
        if len(rows) > 0:
            #update book
            g.cursor.execute('UPDATE balance SET amount = {} WHERE username = \'{}\' and book = \'{}\''.format(amount,session.get('user_id'),book))
        else:
            #insert book
            g.cursor.execute('INSERT into balance VALUES (\'{}\',\'{}\',{})'.format(session.get('user_id'),book,amount))
        return redirect(url_for('bets.add_get_Balance'))

@bp.route('/getBets', methods = ('GET'))
@login_required
def getBets():
    username = session.get('user_id')
    get_db()
    g.cursor.execute('select * from spread_bets where username = \'{}\' and settled = 1'.format(username))
    settled_sp_bets_rows = g.cursor.fetchall()
    g.cursor.execute('select * from spread_bets where username = \'{}\' and settled = 0'.format(username))
    nonsettled_sp_bets_rows = g.cursor.fetchall()
    g.cursor.execute('select * from ml_bets where username = \'{}\' and settled = 1'.format(username))
    settled_ml_bets_rows = g.cursor.fetchall()
    g.cursor.execute('select * from ml_bets where username = \'{}\' and settled = 0'.format(username))
    nonsettled_ml_bets_rows = g.cursor.fetchall()
    d = reformatBets(settled_ml_bets_rows, settled_sp_bets_rows,nonsettled_ml_bets_rows,nonsettled_sp_bets_rows)
    return render_template('bets/display_bets.html', data=d)


# data
    #nonsettled
            #game id
                #ml
                    #list of dicts
                #sp
                    #list of dicts
    #settled
            #game id
                #ml
                    #list of dicts
                #sp
                    #list of dicts
                #score
                    #dict