from flask import g

def reformatSpreadsQueryResult(rows):
    spread_dict = {}
    for row in rows:
        id = row[0]
        if id in spread_dict:
            #game in dict
            bookie_dict = spread_dict[id][3]
            book = row[8]
            bookie_dict[book] = {'ht_spread':float(row[3]), 'ht_line': float(row[4]), 'at_spread': float(row[6]), 'at_line':float(row[7])}
        else:
            #game not in dict
            ht = row[2]
            at = row[5]
            book = row[8]
            start = row[9]
            bookie_dict = {}
            l = [ht,at,start,bookie_dict]
            bookie_dict[book] = {'ht_spread':float(row[3]), 'ht_line': float(row[4]), 'at_spread': float(row[6]), 'at_line':float(row[7])}
            spread_dict[id] = l
    return spread_dict

def reformatMLQueryResult(rows):
    ml_dict = {}
    for row in rows:
        id = row[0]
        if id in ml_dict:
            #game in dict
            bookie_dict = ml_dict[id][3]
            bookie_dict[row[6]] = {'ht_line': float(row[3]), 'at_line':float(row[5])}
        else:
            #game not in dict
            ht  = row[2]
            at = row[4]
            start = row[7]
            bookie_dict = {}
            l = [ht,at,start,bookie_dict]
            bookie_dict[row[6]] = {'ht_line': float(row[3]), 'at_line':float(row[5])}
            ml_dict[id] = l
    return ml_dict

def reformatSettledBets(settled_ml, settled_sp):
    settled = {}
    #settled
        #game id
            #ml
                #list of dicts
            #sp
                #list of dicts
            #score
                #dict
    
    for row in settled_ml:
        id = row[0]
        bet_on = row[2]
        book = row[3]
        line = row[5]
        amt = row[4]
        if id in settled and 'ml' in settled[id]:
            #processed a  ml bet on this game before
            settled[id]['ml'].append({'bet_on': bet_on, 'book': book, 'line': line, 'amt':amt})
        elif id in settled:
            #first ml bet on this game but have bet spread
            settled[id]['ml']=  [{'bet_on': bet_on, 'book': book, 'line': line, 'amt':amt}]
        else:
            #have not processed a bet on this game before
            settled[id] =  {}
            settled[id]['ml']=  [{'bet_on': bet_on, 'book': book, 'line': line, 'amt':amt}]

    for row in settled_sp:
        # id VARCHAR(100), sportkey VARCHAR(100),team_bet_on VARCHAR(100), book_bet_at VARCHAR(100), amount_bet FLOAT(7,2), spread_offered FLOAT(7,2), line_offered FLOAT(7,2), username VARCHAR(100), settled INT, CONSTRAINT id_book_team_user PRIMARY KEY (id,team_bet_on,book_bet_at, username))')
        id = row[0]
        bet_on = row[2]
        book = row[3]
        amt = row[4]
        spread = row[5]
        line = row[6]
        if id in settled and 'sp' in settled[id]:
            settled[id]['sp'].append({'bet_on': bet_on, 'book': book, 'spread': spread, 'line': line, 'amt':amt})
        elif id in settled:
            settled[id]['sp'] = [{'bet_on': bet_on, 'book': book, 'spread': spread, 'line': line, 'amt':amt}]
        else:
            settled[id] = {}
            settled[id]['sp'] = [{'bet_on': bet_on, 'book': book, 'spread': spread, 'line': line, 'amt':amt}]

    
    
    for id in settled.keys():
        #scores (id VARCHAR(100), Home_Team VARCHAR(100), Home_Team_Score FLOAT(7,2), Away_Team VARCHAR(100), Away_Team_Score  FLOAT(7,2),  PRIMARY KEY (id))')
        g.cursor.execute('select * from scores where id = \'{}\''.format(id))
        rows = g.cursor.fetchall()
        row = rows[0]
        ht = row[1]
        hts = row[2]
        at = row[3]
        ats = row[4]
        settled[id]['score'] = {'ht':ht,'hts':hts,'at':at,'ats':ats}
    
    return settled

def reformatUnsettledBets(nonsettled_ml,nonsettled_sp):
    nonsettled = {}
    #settled
        #game id
            #ml
                #list of dicts
            #sp
                #list of dicts
            #score
                #dict
    
    
    #nonsettled
        #game id
            #ml
                #list of dicts
            #sp
                #list of dicts
    
    for row in nonsettled_ml:
        id = row[0]
        bet_on = row[2]
        book = row[3]
        line = row[5]
        amt = row[4]
        if id in nonsettled and 'ml' in nonsettled[id]:
            #processed a bet on this game before
            nonsettled[id]['ml'].append({'bet_on': bet_on, 'book': book, 'line': line, 'amt':amt})
        elif id in nonsettled:
            nonsettled[id]['ml']=  [{'bet_on': bet_on, 'book': book, 'line': line, 'amt':amt}]
        else:
            #have not processed a bet on this game before
            nonsettled[id] =  {}
            nonsettled[id]['ml']=  [{'bet_on': bet_on, 'book': book, 'line': line, 'amt':amt}]
    
    for row in nonsettled_sp:
        id = row[0]
        bet_on = row[2]
        book = row[3]
        amt = row[4]
        spread = row[5]
        line = row[6]
        if id in nonsettled and 'sp' in nonsettled[id]:
            nonsettled[id]['sp'].append({'bet_on': bet_on, 'book': book, 'spread': spread, 'line': line, 'amt':amt})
        elif id in nonsettled:
            nonsettled[id]['sp'] = [{'bet_on': bet_on, 'book': book, 'spread': spread, 'line': line, 'amt':amt}]
        else:
            nonsettled[id] = {}
            nonsettled[id]['sp'] = [{'bet_on': bet_on, 'book': book, 'spread': spread, 'line': line, 'amt':amt}]
    
    
    return nonsettled