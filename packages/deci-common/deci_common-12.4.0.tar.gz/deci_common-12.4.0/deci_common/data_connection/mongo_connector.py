from abc import ABC
from typing import TYPE_CHECKING, Any, Dict

from pymongo import MongoClient

from deci_common.abstractions.abstract_logger import ILogger

if TYPE_CHECKING:
    from typing import Optional, Type

    from pymongo.database import Database


class MongoConfiguration(ABC):
    DB_NAME: str
    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str
    AUTHENTICATION_DB_NAME: str  # The database on which to preform the authentication


class MongoConnector(ILogger):
    """
    An abstract MongoDBConnector that operates on a collection (SQL Table equivalent).
    """

    def __init__(self, mongo_db_configuration: "Type[MongoConfiguration]"):
        self._db_config: "Type[MongoConfiguration]" = mongo_db_configuration
        self._client: "Optional[MongoClient[Dict[str, Any]]]" = None
        super().__init__()

    @property
    def db(self) -> "Database[Dict[str, Any]]":
        if self._client is None:
            self._client = self.__create_client()
        return self._client[self._db_config.DB_NAME]

    def __create_client(self) -> "MongoClient[Dict[str, Any]]":
        """
        Creates a new pymongo.MongoClient for DB operations.
        """
        client = MongoClient[Dict[str, Any]](
            host=self._db_config.HOST,
            port=self._db_config.PORT,
            authSource=self._db_config.AUTHENTICATION_DB_NAME,
            username=self._db_config.USERNAME,
            password=self._db_config.PASSWORD,
            uuidRepresentation="pythonLegacy",
            retryWrites=False,
            connect=True,
            tls=True,
        )
        self._logger.debug("Authenticated to db successfully.")

        return client

    def ping(self) -> "Dict[str, Any]":
        return self.db.command("ping")


__all__ = ["MongoConfiguration", "MongoConnector"]
