import sqlite3 as sq
with sq.connect("users.db") as con:
    cur = con.cursor()

    cur.execute(''' CREATE TABLE users (
    user_id INTEGER, 
    username TEXT, 
    name TeXT, 
    surname TEXT, 
    law TEXT
    )''')
