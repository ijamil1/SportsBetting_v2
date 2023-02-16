from flask import g

def processMLBetResults(ls,ht,hts,at,ats):
    for row in ls:
        team_bet_on = row[2]
        book = row[3]
        amt = float(row[4])
        odds = float(row[5])
        if team_bet_on == ht:
            if hts > ats:
                #won bet
                payout = amt * odds
                updateBalance(book,payout)
        elif team_bet_on == at:
            if ats > hts:
                payout = amt * odds
                updateBalance(book,payout)

def processSpreadBetResults(ls, ht, hts, at, ats):
    # spread_bets (id VARCHAR(100), sportkey VARCHAR(100),team_bet_on VARCHAR(100), book_bet_at VARCHAR(100), amount_bet FLOAT(7,2), spread_offered FLOAT(7,2), line_offered FLOAT(7,2), CONSTRAINT id_book_team PRIMARY KEY (id,team_bet_on,book_bet_at))')

    for row in ls:
        team_bet_on = row[2]
        book = row[3]
        amt = float(row[4])
        spread = float(row[5])
        price = float(row[6])

        if team_bet_on == ht:
            if spread > 0:
                if ats-hts < spread:
                    #won bet!
                    payout = amt * price 
                    updateBalance(book,payout)
            elif spread < 0:
                spread = -1*spread
                if hts - ats > spread:
                    #won bet
                    payout = amt * price 
                    updateBalance(book,payout)
        elif team_bet_on == at:
            if spread > 0:
                if hts-ats < spread:
                    #won bet!
                    payout = amt * price 
                    updateBalance(book,payout)
            elif spread < 0:
                spread = -1*spread
                if ats - hts > spread:
                    #won bet
                    payout = amt * price 
                    updateBalance(book,payout)

def updateBalance(book, amount):
    g.cursor.execute('select amount from balance where book = \'{}\' and  username = \'{}\''.format(book, session.get('user_id')))
    row = g.cursor.fetchall()
    cur_amt = float(row[0][0])
    new_amt = cur_amt + amount
    g.cursor.execute('update balance set amount = {} where book = \'{}\' and username = \'{}\''.format(new_amt,book,session.get('user_id')))
