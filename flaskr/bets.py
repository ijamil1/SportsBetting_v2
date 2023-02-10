from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.helper_funcs import get_db, get_inseason_sports, uploadMLodds, uploadSpreads, deleteML, deleteSpreads,uploadScores, reformatMLQueryResult, reformatSpreadsQueryResult
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