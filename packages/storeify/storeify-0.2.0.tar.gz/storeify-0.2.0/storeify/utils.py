from . import Store, FileCreationError
import random


def generate_valid_key(store: Store) -> str:
    attempts = 100
    for _ in range(attempts):
        key = random.randbytes(16).hex().removeprefix("0x")
        if not store.exists(key):
            return key

    raise FileCreationError("Could not generate a valid key after 100 attempts")
