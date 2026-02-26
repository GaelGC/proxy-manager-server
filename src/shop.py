from sqlite3 import IntegrityError, Row
from src.db import open_db

conn = open_db()
conn.row_factory = Row
cur = conn.cursor()

def add_shop(name, url, proxy_bound=None, description=None):
    try:
        cur.execute("""
            INSERT INTO shops (name, url, description, proxy_bound)
            VALUES (?, ?, ?, ?)""", (name, url, description, proxy_bound))
    except IntegrityError as e:
        conn.rollback()
        if e.args[0] == "UNIQUE constraint failed: shops.name":
            return (False, "A shop with that name already exists")
        elif e.args[0] == "UNIQUE constraint failed: shops.url":
            return (False, "A shop with that URL already exists")
        raise
    conn.commit()
    return (True, "Shop added successfully.")

def list_shop_names():
    rows = cur.execute("SELECT name FROM shops").fetchall()
    if not rows:
        rows = []
    return [row["name"] for row in rows]

def list_pending_items(shop_name):
    rows = cur.execute("""
        SELECT item.id
        FROM items AS item
        INNER JOIN shops AS shop
        ON shop.id = item.shop_id
        WHERE shop.name = ?""", (name,)
    )

    if not rows:
        rows = []
    return [row["id"] for row in rows]

def find_from_name(name):
    row = cur.execute(
            "SELECT id from shops WHERE name = ?", (name,)).fetchone()
    if not row:
        return None
    return row["id"]
