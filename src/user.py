from sqlite3 import IntegrityError, Row
from src.db import open_db
import bcrypt

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
    return (True, "TODO: generate a session here")
