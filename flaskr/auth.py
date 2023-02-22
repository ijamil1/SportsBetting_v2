import functools
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
        g.user = 1
        


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        helper_funcs.get_db()
        username = request.form['username']
        password = request.form['password']
        cursor = g.cursor
        error = None
        cursor.execute('select username from users')
        unames = []
        rows = cursor.fetchall()
        for row in rows:
            unames.append(row[0])
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif username in unames:
            error = 'Username already taken'
        if error is None:
            cursor.execute("INSERT INTO users (username, password) VALUES (\'{}\', \'{}\')".format(username,password))
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("auth.register"))
                

    return render_template('auth/register.html')


@bp.route('/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        helper_funcs.get_db()
        cursor = g.cursor
        error = None
        cursor.execute('SELECT * FROM users WHERE username = \'{}\''.format(username))
        user = cursor.fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif user[2]!=password:
            error = 'Incorrect password.'

        if error is None:
            session['user_id'] = user[1] #actually username
            return redirect(url_for('bets.index'))

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
    return redirect(url_for('.login'))