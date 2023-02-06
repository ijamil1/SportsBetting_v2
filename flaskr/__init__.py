import os
import requests
import pymysql
import datetime 
from flask import Flask, session
from . import auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
  
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import auth, blog 
    app.register_blueprint(auth.bp)
    #app.register_blueprint(blog.bp)
    #app.add_url_rule('/', endpoint='index')

    return app

def init_app(app):
    app.teardown_appcontext(auth.close_db)