import os
from flask import Flask, session
from . import auth, bets, miscellaneous_funcs


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
  
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import auth 
    app.register_blueprint(auth.bp)
    app.register_blueprint(bets.bp)
    miscellaneous_funcs.init_app(app)

    return app
