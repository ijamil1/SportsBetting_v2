import sqlite3
import datetime
import requests
import pymysql
from flask import (
   g, current_app
)

def init_app(app):
    app.teardown_appcontext(close_db)

def create_scores_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS scores (id VARCHAR(100), Home_Team VARCHAR(100), Home_Team_Score FLOAT(7,2), Away_Team VARCHAR(100), Away_Team_Score  FLOAT(7,2),  PRIMARY KEY (id))')

def create_ML_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS moneyline (id VARCHAR(100), sport_key VARCHAR(50), Home_Team VARCHAR(100), Home_Team_Dec_Odds FLOAT(7,2), Away_Team VARCHAR(100), Away_Team_Dec_Odds FLOAT(7,2), book  VARCHAR(50), Start_Time DATETIME, Insert_Time DATETIME, CONSTRAINT id_book_time PRIMARY KEY (id,book, Insert_Time))')
    
def create_spreads_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS spreads (id VARCHAR(100), sport_key VARCHAR(50), Home_Team VARCHAR(100), Home_Team_Spread FLOAT(7,2), Home_Team_Odds FLOAT(7,2), Away_Team VARCHAR(100), Away_Team_Spread FLOAT(7,2), Away_Team_Odds FLOAT(7,2), book  VARCHAR(50), Start_Time DATETIME, Insert_Time DATETIME, CONSTRAINT id_book_time PRIMARY KEY (id,book, Insert_Time))')

def create_balance_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS balance (book VARCHAR(50), amount FLOAT(7,2))')

def createSpreadBetsTable(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS spread_bets (id VARCHAR(100),team_bet_on VARCHAR(100), book_bet_at VARCHAR(100), amount_bet FLOAT(7,2), spread_offered FLOAT(7,2), line_offered FLOAT(7,2), CONSTRAINT id_book_team PRIMARY KEY (id,team_bet_on,book_bet_at))')

def createMLBetsTable(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS ml_bets (id VARCHAR(100),team_bet_on VARCHAR(100), book_bet_at VARCHAR(100), amount_bet FLOAT(7,2), line_offered FLOAT(7,2), CONSTRAINT id_book_team PRIMARY KEY (id,team_bet_on,book_bet_at))')

def create_users_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER AUTO_INCREMENT, username VARCHAR(100), password VARCHAR(100), PRIMARY KEY (id))')

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

def uploadMLodds(sport_key, api_endpoint,  apikey):
    json = requests.get(api_endpoint+sport_key+'/odds/', params = {'apiKey':apikey,'regions':'us','markets':'h2h'}).json()
    get_db()
    mybooks = current_app.config['MY_BOOKS'].split(',')
    for game in json:
        game_id = game['id']
        home_team = game['home_team']
        away_team = game['away_team']
        start_time = datetime.datetime.fromisoformat(game['commence_time'][:-1]+'+00:00') #utc start_time 
        bookies = game['bookmakers']
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
            if utc_now < start_time and not check_for_ml_dups(game_id,ht_price,at_price,book_name):
                g.cursor.execute('DELETE from moneyline where id = \'{}\' and book = \'{}\''.format(game_id,book_name))
                ls_commencetime =  game['commence_time'].split('T')
                start_time_str = ls_commencetime[0] + ' ' + ls_commencetime[1][:-1]
                utc_now_str = utc_now.strftime('%Y-%m-%d %H:%M:%S')
                g.cursor.execute('INSERT into moneyline VALUES (\'{}\',\'{}\',\'{}\',{},\'{}\',{},\'{}\',\'{}\',\'{}\')'.format(game_id,sport_key,home_team,ht_price,away_team, at_price, book_name, start_time_str, utc_now_str))

def uploadSpreads(sport_key, api_endpoint, apikey):
    json = requests.get(api_endpoint+sport_key+'/odds/', params = {'apiKey':apikey,'regions':'us','markets':'spreads'}).json()
    get_db()
    mybooks = current_app.config['MY_BOOKS'].split(',')
    for game in json:
        id = game['id']
        start_time = datetime.datetime.fromisoformat(game['commence_time'][:-1]+'+00:00')
        ht = game['home_team']
        at = game['away_team']
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
            if utc_now < start_time and not check_for_sp_dups(id,home_spread,home_price,away_spread,away_price,book):
                g.cursor.execute('DELETE from spreads where id = \'{}\' and book = \'{}\''.format(id,book))
                ls_commencetime =  game['commence_time'].split('T')
                start_time_str = ls_commencetime[0] + ' ' + ls_commencetime[1][:-1]
                utc_now_str = utc_now.strftime('%Y-%m-%d %H:%M:%S')
                g.cursor.execute('INSERT into spreads VALUES (\'{}\',\'{}\',\'{}\',{},{},\'{}\',{},{},\'{}\',\'{}\',\'{}\')'.format(id,sport_key,ht,home_spread,home_price,at,away_spread,away_price,book, start_time_str, utc_now_str)) 

def check_for_sp_dups(game_id, home_spread, home_price, away_spread, away_price,book):
    query = 'select Home_Team_Spread, Away_Team_Spread, Home_Team_Odds, Away_Team_Odds from spreads where id = \'{}\' and book = \'{}\''.format(game_id,book)
    g.cursor.execute(query)
    data = g.cursor.fetchall()
    if data is None:
        return False #no dups
    elif len(data) == 0:
        return False #no dups
    else:
        for row in data:
            existing_home_spread = float(row[0])
            existing_away_spread = float(row[1])
            existing_home_odds = float(row[2])
            existing_away_odds = float(row[3])
            if existing_home_spread == float(home_spread):
                if existing_away_spread == float(away_spread):
                    if abs(float(home_price)-existing_home_odds)/existing_home_odds < .01:
                        if abs(float(away_price)-existing_away_odds)/existing_away_odds < .01:
                            return True
            return False


def check_for_ml_dups(game_id, ht_price, at_price, book):
    query = 'select Home_Team_Dec_Odds, Away_Team_Dec_Odds from moneyline where id = \'{}\' and book = \'{}\''.format(game_id,book)
    g.cursor.execute(query)
    data = g.cursor.fetchall()
    if data is None:
        return False #no dups
    elif len(data) == 0:
        return False #no dups
    else:
        for row in data:
            existing_ht_price = float(row[0])
            existing_at_price = float(row[1])
            if abs(float(ht_price)-existing_ht_price)/existing_ht_price < .01:
                if abs(float(at_price)-existing_at_price)/existing_at_price < .01:
                    return True
            return False
