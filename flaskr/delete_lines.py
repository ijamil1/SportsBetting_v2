import datetime 
from flask import g
from flaskr.scoring_helper_funcs import getIdsScoresTbl

def deleteSpreads():
    existing_ids = getIdsScoresTbl()
    l = ''
    for id in existing_ids:
        l+='\''+id+'\','
    l = l[:-1]
    query = 'DELETE from spreads where id in({})'.format(l)
    g.cursor.execute(query)

def deleteML():
    existing_ids = getIdsScoresTbl()
    l = ''
    for id in existing_ids:
        l+='\''+id+'\','
    l = l[:-1]
    query = 'DELETE from moneyline where id in ({})'.format(l)
    g.cursor.execute(query)