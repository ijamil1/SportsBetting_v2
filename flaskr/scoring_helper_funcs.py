import requests
from flaskr.process_bets import *
from flask import (g, session, current_app)


def getIdsScoresTbl():
    g.cursor.execute('select id from scores')
    rows = g.cursor.fetchall()
    ls = []
    for row in rows:
        ls.append(row[0])
    return ls   

def uploadScores():
    #gets the ids and sportkeys of games I've bet on; loops thru sportkeys and retrieves scores for each sport; for each sport, loops thru completed games 
    #, checks that we bet on this game and that the game is not already in the score table, and then queries the bets we made on the game and updates  
    # the balances accordingly; it also uploads the score to a score table;
    # this function runs each time that the user logs in
    username = session.get('user_id')
    spread_ids = []
    ml_ids = []
    bet_on_ids = []
    bet_on_sportkeys = []
    g.cursor.execute('SELECT id, sportkey from ml_bets where username = \'{}\' and settled = 0'.format(username))
    rows = g.cursor.fetchall()
    for row in rows:
        if row[0] not in ml_ids:
            ml_ids.append(row[0])
        if row[1] not in bet_on_sportkeys:
            bet_on_sportkeys.append(row[1])
    g.cursor.execute('SELECT id, sportkey from spread_bets where username = \'{}\' and settled = 0'.format(username))
    rows = g.cursor.fetchall()
    for row in rows:
        if row[0] not in spread_ids:
            spread_ids.append(row[0])
        if row[1] not in bet_on_sportkeys:
            bet_on_sportkeys.append(row[1])

    score_ids = getIdsScoresTbl()
    bet_on_ids = set(ml_ids).union(spread_ids) #games bet on by user that have not been settled yet

    for key in bet_on_sportkeys:
        json = requests.get(current_app.config['API']+key+'/scores/',params={'apiKey':current_app.config['APIKEY'],'daysFrom':3}).json()
        ht = ''
        at = ''
        ht_score = -1
        at_score = -1
        for game in json:
            if game['completed'] and (game['id'] in bet_on_ids):
                scores = game['scores']
                for score in scores:
                    cur_team = score['name']
                    cur_score = score['score']
                    if cur_team == game['home_team']:
                        ht = cur_team
                        ht_score = float(cur_score)
                    elif cur_team == game['away_team']:
                        at = cur_team
                        at_score = float(cur_score)
                if game['id'] in spread_ids:
                    g.cursor.execute('select * from spread_bets where id = \'{}\' and username = \'{}\' and settled = 0'.format(game['id'],username))
                    rows = g.cursor.fetchall()
                    processSpreadBetResults(rows, ht, ht_score, at, at_score)
                    settleBets(rows,'sp')
                if game['id'] in ml_ids:
                    g.cursor.execute('select * from ml_bets where id = \'{}\' and username = \'{}\' and settled = 0'.format(game['id'],username))
                    rows = g.cursor.fetchall()
                    processMLBetResults(rows,ht,ht_score,at,at_score)
                    settleBets(rows, 'ml')
                if game['id'] not in score_ids:
                    g.cursor.execute('INSERT INTO scores VALUES (\'{}\',\'{}\',{},\'{}\',{})'.format(game['id'],ht,ht_score,at,at_score))

def settleBets(data, type_of_bet):
    if type_of_bet == 'ml':
        for row in data:
            id = row[0]
            username = session.get('user_id')
            g.cursor.execute('UPDATE ml_bets SET settled = 1 WHERE id = \'{}\' and username = \'{}\''.format(id,username))
    else:
        for row in data:
            id = row[0]
            username = session.get('user_id')
            g.cursor.execute('UPDATE spread_bets SET settled = 1 WHERE id = \'{}\' and username = \'{}\''.format(id,username))
