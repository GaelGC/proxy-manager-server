import os
import sqlite3

DB_PATH_ENVNAME = "DB_PATH"

def open_db():
    db = sqlite3.connect(os.environ.get(DB_PATH_ENVNAME, "db/db.db"))
    db.execute("PRAGMA foreign_keys = ON;")
    return db

def db_setup(conn):
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS db_version (version INTEGER)")

    # Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER      PRIMARY KEY   AUTOINCREMENT,
            login     VARCHAR(256) NOT NULL      UNIQUE,
            pass_hash VARCHAR(256) NOT NULL,
            is_admin  BOOLEAN      DEFAULT FALSE
        )
    """)

    # User sessions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            cookie     TEXT    NOT NULL UNIQUE PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            expires_at TEXT    NOT NULL
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_cookie ON sessions(cookie);")


    # Shops we can buy from
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id           INTEGER      PRIMARY KEY AUTOINCREMENT,
            name         VARCHAR(256) NOT NULL    UNIQUE,
            url          TEXT         NOT NULL    UNIQUE,
            description  TEXT,
            proxy_bound  BOOLEAN
        )
    """)

    # Transaction-level orders done to shop.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shop_orders (
            id            INTEGER       PRIMARY KEY AUTOINCREMENT,
            shop_id       INTEGER       NOT NULL,

            name          VARCHAR(256)  NOT NULL,
            tracking_name VARCHAR(256),
            shipping_yen  INTEGER,
            total_eur     INTEGER,
            status        VARCHAR(16),

            FOREIGN KEY(shop_id) REFERENCES shops(id),

            CHECK(status IN ("todo",      "failure", "ongoing", "done",
                             "cancelled", "deleted"))
        )
    """)

    # Package in the warehouse. relative_id may be either the parent (split)
    # or the child (consolidation).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS warehouse_parcels (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            parcel_id   TEXT UNIQUE,

            relative_id INTEGER,
            type        VARCHAR(16),

            width          FLOAT,
            height         FLOAT,
            length         FLOAT,
            weight         FLOAT,

            FOREIGN KEY(relative_id) REFERENCES warehouse_parcels(id),

            CHECK(type IN ("received", "split", "consolidation"))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS out_parcels (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_id   INTEGER,

            tracking_name  VARCHAR(256),
            status         VARCHAR(16),

            FOREIGN KEY(warehouse_id) REFERENCES warehouse_parcels(id),

            CHECK(status IN ("shipped", "received", "deleted"))
        )
    """)


    # Parcel-level shop orders.
    # One order may have been splat in several parcels by the shop.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS in_parcels (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id       INTEGER NOT NULL,
            warehouse_id   INTEGER,

            tracking_name  VARCHAR(256),
            status         VARCHAR(16),

            FOREIGN KEY(order_id) REFERENCES shop_orders(id),
            FOREIGN KEY(warehouse_id) REFERENCES warehouse_parcels(id),

            CHECK(status IN ("shipped", "received", "deleted"))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id             INTEGER       PRIMARY KEY AUTOINCREMENT,
            requester_id   INTEGER       NOT NULL,
            shop_id        INTEGER       NOT NULL,
            in_parcel_id   INTEGER,

            name           VARCHAR(256)  NOT NULL,
            description    TEXT,
            url            TEXT          NOT NULL,
            price_yen      INTEGER       NOT NULL,
            price_euro     INTEGER,
            status         VARCHAR(16)   DEFAULT "todo",
            refusal_reason TEXT,
            read_only      BOOLEAN       DEFAULT FALSE,
            width          FLOAT,
            height         FLOAT,
            length         FLOAT,
            weight         FLOAT,

            CHECK(status IN ("todo",    "bought",  "warehouse", "consolidating",
                             "shipped", "done",    "refused",   "deleted")),
            CHECK(price_yen > 0)

            FOREIGN KEY(requester_id) REFERENCES users(id),
            FOREIGN KEY(shop_id)      REFERENCES shops(id),
            FOREIGN KEY(in_parcel_id) REFERENCES in_parcels(id)
        )
    """)
    conn.commit()
    cur.close()

def fake_db_setup():
    if os.environ.get('IS_TEST', '0') != '1':
        print('WARNING: This command will wipe your database. If indeed trying to run in test mode, set IS_TEST=1')
        exit(1)
    if os.environ[DB_PATH_ENVNAME] != "db/test.db":
        print('For tests, as a safety measure, DB MUST be set to db/test.db')
    conn = open_db()
    cur = conn.cursor()
    cur.execute("PRAGMA writable_schema = 1;")
    cur.execute("DELETE FROM sqlite_master;")
    cur.execute("PRAGMA writable_schema = 0;")
    conn.commit()
    cur.execute("VACUUM;")
    cur.execute("PRAGMA integrity_check;")
    db_setup(conn)
    conn.close()

conn = open_db()
db_setup(conn)
conn.close()
