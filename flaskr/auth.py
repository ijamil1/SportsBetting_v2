import functools
import pymysql 
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from . import helper_funcs

bp = Blueprint('auth', __name__)

@bp.before_app_request
def load_logged_in_user_and_create_db_conn():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = session.get('cursor').execute(
            'SELECT * FROM users WHERE id = {}'.format(int(user_id))
        ).fetchone()
    

def get_db():
    g.connection = pymysql.connect(host = current_app.config['DBENDPOINT'], user = current_app.config['USERNAME'], password = current_app.config['PW'], database = current_app.config['DB'], autocommit=True)
    g.cursor = g.connection.cursor()
    helper_funcs.create_scores_table(g.cursor)
    helper_funcs.create_ML_table(g.cursor)
    helper_funcs.create_spreads_table(g.cursor)
    helper_funcs.create_balance_table(g.cursor)
    helper_funcs.createSpreadBetsTable(g.cursor)
    helper_funcs.createMLBetsTable(g.cursor)
    helper_funcs.create_users_table(g.cursor)
    return g.cursor

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        if error is None:
            cursor = get_db()
            cursor.execute("INSERT INTO users (username, password) VALUES (\'{}\', \'{}\')".format(username,password))
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("auth.register"))
                

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = get_db()
        error = None
        cursor.execute('SELECT * FROM users WHERE username = \'{}\''.format(username))
        user = cursor.fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif user[2]!=password:
            error = 'Incorrect password.'

        if error is None:
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))