import sqlite3

def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d