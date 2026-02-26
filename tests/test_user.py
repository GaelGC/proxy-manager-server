import pytest

from src.user import create_user, authenticate, get_user_id
from src.db import fake_db_setup, open_db

@pytest.mark.dependency()
def test_user_creation():
    fake_db_setup()
    assert create_user("user1", "aaa")[0]
    assert create_user("user2", "bbb")[0]
    assert not create_user("user2", "ccc")[0]

@pytest.mark.dependency(depends=["test_user_creation"])
def test_basic_user_authentication():
    fake_db_setup()
    create_user("user1", "aaa")
    create_user("user2", "bbb")
    assert not authenticate("nouser", "aaa")[0]
    assert not authenticate("user2", "aaa")[0]
    auth1 = authenticate("user1", "aaa")
    auth2 = authenticate("user1", "aaa")
    auth3 = authenticate("user2", "bbb")
    assert auth1[0]
    assert auth2[0]
    assert auth3[0]
    assert auth1[1] != auth2[1]
    assert auth1[1] != auth3[1]
    assert auth2[1] != auth3[1]

@pytest.mark.dependency(depends=["test_basic_user_authentication"])
def test_session():
    fake_db_setup()
    create_user("user1", "aaa")
    create_user("user2", "bbb")
    auth = authenticate("user1", "aaa")[1]
    auth2 = authenticate("user1", "aaa")[1]
    auth3 = authenticate("user2", "bbb")[1]
    assert get_user_id(auth) == 1
    assert get_user_id(auth2) == 1
    assert get_user_id(auth3) == 2
    assert get_user_id("toto") is None
    conn = open_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE sessions SET expires_at = datetime('now', '-2 months')
        WHERE cookie = ?
    """, (auth,))
    conn.commit()
    cur.close()
    conn.close()
    assert get_user_id(auth) is None
