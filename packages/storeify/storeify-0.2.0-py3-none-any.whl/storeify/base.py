from .errors import FileCreationError, OutOfSpace
from io import BytesIO
from typing import Protocol
from random import randint
from abc import ABC, abstractmethod


class BasicStore(ABC):
    @abstractmethod
    def create(self, data: "bytes|BytesIO") -> str:
        """_description_

        Args:
            data (bytes|BytesIO): _description_

        Raises:
            CreationError: _description_
            OutOfSpace: _description_

        Returns:
            str: _description_
        """
        ...


    @abstractmethod
    def get(self, key: str) -> BytesIO:
        """_description_

        Args:
            key (str): _description_

        Raises:
            FileNotFoundError: _description_

        Returns:
            str: _description_
        """
        ...


class Store(BasicStore):
    """
    - Stores may encode keys, however they should be decoded when returned to the user
    """
    @abstractmethod
    def put(self, key: str, data: "bytes|BytesIO", *, upsert: bool = False):
        """_description_

        Args:
            key (str): The key to store the data under
            data (bytes|BytesIO): The buffer to store
            upsert (bool): Replace file if it already exists

        Raises:
            FileExistsError: if upsert is False and the file already exists
        """
        ...


    @abstractmethod
    def exists(self, key: str) -> bool:
        """Checks if an entry exists

        Args:
            key (str): _description_

        Raises:
            FileExistsError: if upsert is False and the file already exists

        Returns:
            bool: _description_
        """
        ...


    @abstractmethod
    def delete(self, key: str):
        """Deletes an entry using it's key
        If the file does not exist, this method should do nothing

        Args:
            key (str): The entry to delete
        """
        ...


    @abstractmethod
    def list(self) -> list[str]:
        """List all keys in the store

        Returns:
            list[str]: A list of keys
        """
        ...


class CDNStore(ABC):
    @abstractmethod
    def url(self, key: str) -> str:
        """Generates a publicly accessible URL for a file

        Args:
            filename (str): _description_

        Returns:
            str: _description_
        """
        ...
