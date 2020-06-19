from pullframe.persist import PERSIST
from pullframe.types import CacheFormat


def test_cache_type_includes_all():
    assert set(PERSIST.keys()) == set(i.value for i in CacheFormat)
