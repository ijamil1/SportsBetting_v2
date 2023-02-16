import datetime 
from flask import g

def deleteSpreads():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    utc_now_str = utc_now.strftime('%Y-%m-%d %H:%M:%S')
    query = 'DELETE from spreads where TIMESTAMPADD(DAY,4,Start_Time) < \'{}\''.format(utc_now_str)
    g.cursor.execute(query)

def deleteML():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    utc_now_str = utc_now.strftime('%Y-%m-%d %H:%M:%S')
    query = 'DELETE from moneyline where TIMESTAMPADD(DAY,4,Start_Time) < \'{}\''.format(utc_now_str)
    g.cursor.execute(query)