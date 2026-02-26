import pytest

from src.shop import add_shop, list_shop_names, find_from_name
from src.db import fake_db_setup, open_db

@pytest.mark.dependency(name="test_shop_creation")
def test_shop_creation():
    fake_db_setup()
    assert add_shop("rakuten", "http://blablbla")[0]
    assert not add_shop("rakuten", "http://blablbla2")[0]
    assert not add_shop("rakuten2", "http://blablbla")[0]
    assert add_shop("rakuten2", "http://blablbla2")[0]

@pytest.mark.dependency(depends=["test_shop_creation"],
    name="test_shop_name_listing")
def test_shop_name_listing():
    fake_db_setup()
    add_shop("rakuten", "http://blablbla")[0]
    add_shop("rakuten2", "http://blablbla2")[0]
    names = list_shop_names()
    assert len(names) == 2
    assert "rakuten" in names
    assert "rakuten2" in names

@pytest.mark.dependency(depends=["test_shop_creation"],
    name="test_shop_name_lookup")
def test_shop_name_lookup():
    fake_db_setup()
    add_shop("rakuten", "http://blablbla")[0]
    add_shop("rakuten2", "http://blablbla2")[0]
    assert find_from_name("rakuten") == 1
    assert find_from_name("rakuten2") == 2
    assert find_from_name("rakuten3") is None
