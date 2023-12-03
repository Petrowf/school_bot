import sqlite3 as sq

with sq.connect('users.db') as con:#создание бд
    cur = con.cursor() #курсор
    cur.execute(""" TABLE users (
    id INTEGER,
    chatid INTEGER,
    name TEXT,
    surname TEXT,
    law TEXT
    )""")