from . import Store, generate_valid_key
from io import BytesIO


def assert_not_exists(store: Store, key: str, upsert: bool):
    if not upsert and store.exists(key):
        raise FileExistsError("File already exists")


def generic_create_file(store: Store, data: "bytes|BytesIO") -> str:
    key = generate_valid_key(store)
    store.put(key, data)
    return key

def convert_to_buffer(data: "bytes|BytesIO") -> BytesIO:
    if isinstance(data, BytesIO):
        return data
    else:
        return BytesIO(data)


def convert_to_bytes(data: "bytes|BytesIO") -> bytes:
    if isinstance(data, bytes):
        return data
    else:
        return data.read()
