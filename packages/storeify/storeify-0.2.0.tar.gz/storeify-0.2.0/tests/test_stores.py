from storeify import Store, MemoryStore, FileStore, generate_valid_key
import pytest

stores = [
    MemoryStore(),
    FileStore("./data"),
]
get_class_name = lambda store: store.__class__.__name__


@pytest.mark.parametrize("store", stores, ids=get_class_name)
def test_put(store: Store):
    key = generate_valid_key(store)
    store.put(key, b"hello world")
    assert store.exists(key)
    data = store.get(key).read()
    assert data == b"hello world"


@pytest.mark.parametrize("store", stores, ids=get_class_name)
def test_delete(store: Store):
    key = generate_valid_key(store)
    store.put(key, b"hello world")
    assert store.exists(key)
    store.delete(key)
    assert not store.exists(key)
