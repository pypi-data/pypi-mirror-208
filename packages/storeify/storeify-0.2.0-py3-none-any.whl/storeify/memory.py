from . import Store, shared
from io import BytesIO


class MemoryStore(Store):
    _store: dict[str, bytes]

    def __init__(self):
        self._store = {}


    def create(self, data: "bytes|BytesIO") -> str:
        return shared.generic_create_file(self, data)


    def put(self, key: str, data: "bytes|BytesIO", *, upsert: bool = False):
        shared.assert_not_exists(self, key, upsert)
        data = shared.convert_to_bytes(data)
        self._store[key] = data


    def get(self, key: str) -> BytesIO:
        data = self._store[key]
        return BytesIO(data)


    def delete(self, key: str):
        del self._store[key]


    def exists(self, key: str) -> bool:
        return key in self._store


    def list(self) -> list[str]:
        return list(self._store.keys())
