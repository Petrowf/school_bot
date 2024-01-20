import sqlite3 as sq
con = sq.connect("events.db")
cur = con.cursor()
cur.execute("""CREATE TABLE 'events' ( 
        name TEXT, 
        time_start DATATIME,
        time_end DATATIME,
        contact_person TEXT, 
        tg_teg TEXT
        )""")
con.commit()