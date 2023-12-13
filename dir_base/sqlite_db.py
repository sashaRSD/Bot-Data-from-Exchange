import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('dir_base/base.db')
    cur = base.cursor()
    if base:
        print('Data base connect OK!')
    base.execute('CREATE TABLE IF NOT EXISTS data(id INT PRIMARY KEY, stock TEXT, cur TEXT, cryptocur TEXT, username TEXT)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO data VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_read(data):
    return cur.execute('SELECT * FROM data WHERE id == ?', (data,)).fetchall()


async def sql_delete_command(data):
    cur.execute('DELETE FROM data WHERE id == ?', (data,))
    base.commit()


