#placeholder comment
import requests
import pymysql
from flaskr.create_tbls import *
from flask import (
   g, current_app, session
)

def init_app(app):
    app.teardown_appcontext(close_db)

def get_db():
    g.connection = pymysql.connect(host = current_app.config['DBENDPOINT'], user = current_app.config['USERNAME'], password = current_app.config['PW'], database = current_app.config['DB'], autocommit=True)
    g.cursor = g.connection.cursor()
    create_scores_table(g.cursor)
    create_ML_table(g.cursor)
    create_spreads_table(g.cursor)
    create_balance_table(g.cursor)
    createSpreadBetsTable(g.cursor)
    createMLBetsTable(g.cursor)
    create_users_table(g.cursor)

def close_db(e=None):
    db = g.pop('connection', None)

    if db is not None:
        db.close()

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
 



