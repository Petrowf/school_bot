import sqlite3 as sq

def proverka_prav(message, cur, con):
    query = f'SELECT name FROM users WHERE id={id}'
    cur.execute(query)
    us_name = cur.fetchone()
    last_name = message.from_user.last_name
    first_name = message.from_user.first_name
    chat_id = message.chat.id
    id = message.from_user.id
    access = 'common'
    if us_name == None:
        f'INSERT INTO users VALUES({id, chat_id, us_name, first_name, last_name, access})'


if __name__ == "__main__":
    con = sq.connect('users.db')
    cur = con.cursor()
    print(proverka_prav(46216752416, cur, con))