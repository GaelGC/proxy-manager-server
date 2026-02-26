from sqlite3 import IntegrityError, Row
from src.db import open_db
from datetime import datetime, timedelta, timezone
import bcrypt
import secrets

conn = open_db()
conn.row_factory = Row
cur = conn.cursor()

def create_user(login, password, is_admin=False):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password, salt)

    try:
        cur.execute("INSERT INTO users (login, pass_hash, is_admin) VALUES (?, ?, ?)",
                    (login, password, is_admin))
    except IntegrityError as e:
        conn.rollback()
        if e.args[0] == "UNIQUE constraint failed: users.login":
            return (False, "User already exists")
        raise
    conn.commit()
    return (True, "User created successfully.")

def authenticate(login, password):
    valid = False
    password = password.encode('utf-8')
    row = cur.execute("SELECT id, pass_hash from users where login == ?", (login,)).fetchone()
    if row:
        if bcrypt.checkpw(password, row["pass_hash"]):
            valid = True
    if not valid:
        return (False, "User does not exist or password did not match")

    cookie = secrets.token_urlsafe(32)
    cur.execute("INSERT INTO sessions (user_id, cookie, expires_at) VALUES (?, ?, datetime('now', '+1 month'))",
                (row['id'], cookie))
    conn.commit()
    return (True, cookie)

def get_user_id(cookie):
    row = cur.execute("""SELECT user_id from sessions where cookie == ? AND expires_at > datetime('now')""", (cookie,)).fetchone()
    if row:
        return row["user_id"]
    return None

def user_id_from_login(login):
    row = cur.execute("""SELECT id from users where login == ?""", (login,)).fetchone()
    if row:
        return row["id"]
    return None
