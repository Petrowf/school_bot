import sqlite3 as sq

def proverka_prav(user, cur, con, first_name, last_name, chat_id, access):
    query = f'SELECT name FROM users WHERE id={id}'
    us_name = cur.fetchone()
    if us_name == None:
        f'INSERT INTO users VALUES({id, chat_id, us_name, first_name, last_name, access})'


if __name__ == "__main__":
    con = sq.connect('users.db')
    cur = con.cursor()
    print(proverka_prav(46216752416, cur, con))