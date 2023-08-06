from . import Store, shared
from pathlib import Path
from io import BytesIO
from base64 import b64encode, b64decode


class FileStore(Store):
    _store_dir: Path

    def __init__(self, directory: "str | Path"):
        self._store_dir = Path(directory)
        if not self._store_dir.is_dir():
            raise NotADirectoryError(f"{directory} is not a directory")

        self._store_dir.mkdir(parents=True, exist_ok=True)


    def create(self, data: "bytes|BytesIO") -> str:
        return shared.generic_create_file(self, data)


    def get(self, key: str) -> BytesIO:
        path = self._generate_path(key)
        data = path.read_bytes()
        return BytesIO(data)


    def put(self, key: str, data: "bytes|BytesIO", *, upsert: bool = False):
        shared.assert_not_exists(self, key, upsert)
        data = shared.convert_to_bytes(data)
        path = self._generate_path(key)
        path.write_bytes(data)


    def exists(self, key: str) -> bool:
        path = self._generate_path(key)
        return path.exists()


    def delete(self, key: str):
        path = self._generate_path(key)
        path.unlink(missing_ok=True)


    def list(self) -> list[str]:
        return [
            b64decode(path.name).decode()
            for path in self._store_dir.iterdir()
        ]


    def _generate_path(self, filename: str) -> Path:
        filename = b64encode(filename.encode()).decode()
        return Path(self._store_dir, filename)
