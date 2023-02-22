def create_scores_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS scores (id VARCHAR(100), Home_Team VARCHAR(100), Home_Team_Score FLOAT(7,2), Away_Team VARCHAR(100), Away_Team_Score  FLOAT(7,2),  PRIMARY KEY (id))')

def create_ML_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS moneyline (id VARCHAR(100), sport_key VARCHAR(50), Home_Team VARCHAR(100), Home_Team_Dec_Odds FLOAT(7,2), Away_Team VARCHAR(100), Away_Team_Dec_Odds FLOAT(7,2), book  VARCHAR(50), Start_Time DATETIME, Insert_Time DATETIME, CONSTRAINT id_book_time PRIMARY KEY (id,book, Insert_Time))')
    
def create_spreads_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS spreads (id VARCHAR(100), sport_key VARCHAR(50), Home_Team VARCHAR(100), Home_Team_Spread FLOAT(7,2), Home_Team_Odds FLOAT(7,2), Away_Team VARCHAR(100), Away_Team_Spread FLOAT(7,2), Away_Team_Odds FLOAT(7,2), book  VARCHAR(50), Start_Time DATETIME, Insert_Time DATETIME, CONSTRAINT id_book_time PRIMARY KEY (id,book, Insert_Time))')

def create_balance_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS balance (username VARCHAR(100),book VARCHAR(50), amount FLOAT(7,2), CONSTRAINT user_and_book PRIMARY KEY (username,book))')

def createSpreadBetsTable(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS spread_bets (id VARCHAR(100), sportkey VARCHAR(100),team_bet_on VARCHAR(100), book_bet_at VARCHAR(100), amount_bet FLOAT(7,2), spread_offered FLOAT(7,2), line_offered FLOAT(7,2), username VARCHAR(100), settled INT, CONSTRAINT id_book_team_user PRIMARY KEY (id,team_bet_on,book_bet_at, username))')

def createMLBetsTable(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS ml_bets (id VARCHAR(100), sportkey VARCHAR(100),team_bet_on VARCHAR(100), book_bet_at VARCHAR(100), amount_bet FLOAT(7,2), line_offered FLOAT(7,2), username VARCHAR(100), settled INT, CONSTRAINT id_book_team_user PRIMARY KEY (id,team_bet_on,book_bet_at,username))')

def create_users_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER AUTO_INCREMENT, username VARCHAR(100), password VARCHAR(100), PRIMARY KEY (id))')