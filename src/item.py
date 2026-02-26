from sqlite3 import IntegrityError, Row
from src.db import open_db

conn = open_db()
conn.row_factory = Row
cur = conn.cursor()

def add_item(requester, shop, name, url, price_yen):
    try:
        cur.execute("""
            INSERT INTO items (requester_id, shop_id, name, url, price_yen)
            VALUES (?, ?, ?, ?, ?)""",
            (requester, shop, name, url, price_yen))
    except IntegrityError as e:
        conn.rollback()
        if e.args[0] == "FOREIGN KEY constraint failed":
            return (False, "Internal error, unknown shop or user.")
        elif e.args[0] == "CHECK constraint failed: price_yen > 0":
            return (False, "Invalid price, must be >0")
        raise
    conn.commit()
    return (True, "Item added successfully.")
