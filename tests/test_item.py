import pytest

from src.item import add_item
from src.user import create_user, user_id_from_login
from src.shop import add_shop, find_from_name
from src.db import fake_db_setup, open_db

@pytest.mark.dependency(scope="session", name="test_item_creation",
    depends=["test_user_lookup", "test_shop_name_lookup"])
def test_item_creation():
    fake_db_setup()
    create_user("toto", "azerty")
    add_shop("rakuten", "http://toto")
    uid = user_id_from_login("toto")
    sid = find_from_name("rakuten")

    assert add_item(uid, sid, "aaa", "http://aaa", 100)[0]
    assert add_item(uid, sid, "aaa", "http://aaa", 100)[0]
    assert not add_item(uid + 100, sid, "aaa", "http://aaa", 100)[0]
    assert not add_item(uid, sid + 100, "aaa", "http://aaa", 100)[0]
    assert not add_item(uid, sid, "aaa", "http://aaa", 0)[0]
