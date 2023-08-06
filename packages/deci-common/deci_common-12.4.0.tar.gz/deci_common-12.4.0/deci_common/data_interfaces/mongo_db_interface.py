from datetime import datetime
from typing import TYPE_CHECKING
from warnings import warn

from deci_common.abstractions.abstract_logger import ILogger

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional

    from pymongo.collection import Collection
    from pymongo.command_cursor import CommandCursor
    from pymongo.cursor import Cursor
    from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

    from deci_common.data_connection.mongo_connector import MongoConnector


class MongoDBInterface(ILogger):
    # FIXME: https://deci.atlassian.net/browse/PLFM-3408
    _CREATION_TIME = "creation_time"
    _UPDATE_TIME = "update_time"

    def __init__(self, collection: str, mongo_connector: "MongoConnector"):
        super().__init__()
        self._collection = collection
        self._mongo_connector = mongo_connector

    @property
    def collection(self) -> "Collection[Dict[str, Any]]":
        return self._mongo_connector.db[self._collection]

    @property
    def _update_time_partial(self) -> "Dict[str, datetime]":
        return {self._UPDATE_TIME: datetime.utcnow()}

    @property
    def _creation_time_partial(self) -> "Dict[str, datetime]":
        return {self._CREATION_TIME: datetime.utcnow()}

    def delete(self, search_filter: "Dict[str, Any]") -> "DeleteResult":
        """
        Delete documents from the DB that match the passed search_filter.
        @param search_filter: The document to insert
        @return: DeleteResult
        """
        return self.collection.delete_many(search_filter)

    def insert(self, document: "Dict[str, Any]") -> "InsertOneResult":
        """
        Insert a document to the DB.
        @param document: The document to insert
        @return: InsertOneResult
        """
        document.update({**self._creation_time_partial, **self._update_time_partial})
        return self.collection.insert_one(document=document)

    def find_one(
        self,
        search_filter: "Dict[str, Any]",
        *,
        projection: "Dict[str, Any]" = {},
    ) -> "Optional[Dict[str, Any]]":
        """
        Find single element from DB with a specified search filter
        @param search_filter: Filter for the search
        @param projection: Projection to apply
        @return: Dict[str, Any]
        """
        return self.collection.find_one(filter=search_filter, projection=projection)

    def find_by_id(self, _id: "Any", *, id_key: str = "id") -> "Optional[Dict[str, Any]]":
        """
        Find single element from DB by ID
        @param _id: ID value
        @param id_key: Name of field containing ID in DB. Optional, defaults to "id".
        @return: Dict[str, Any]
        """
        return self.find_one(search_filter={id_key: _id})

    def find(
        self,
        search_filter: "Dict[str, Any]" = {},
        *,
        projection: "Dict[str, Any]" = {},
    ) -> "Cursor[Dict[str, Any]]":
        """
        Find all elements from DB with a specified search filter
        @param search_filter: Filter for the search
        @param projection: Projection to apply
        @return: Cursor[Dict[str, Any]
        """
        return self.collection.find(filter=search_filter, projection=projection)

    def _update(
        self,
        *,
        search_filter: "Dict[str, Any]",
        update: "Dict[str, Any]",
        upsert: bool,
    ) -> "UpdateResult":
        """
        Update all elements from DB that match a specified search filter with the updated document
        @param search_filter: Filter for the search
        @param update: Update to apply
        @return: UpdateResult
        """
        return self.collection.update_many(filter=search_filter, update=update, upsert=upsert)

    def update(
        self,
        search_filter: "Dict[str, Any]",
        *,
        updated_document: "Dict[str, Any]",
        upsert: bool = False,
    ) -> "UpdateResult":
        if upsert:
            warn("Passing `upsert=True` is deprecated, please fix usage.")
        updated_document.update(self._update_time_partial)
        return self._update(search_filter=search_filter, update={"$set": updated_document}, upsert=upsert)

    def upsert(self, updated_document: "Dict[str, Any]", *, id_key: str = "id") -> "Dict[str, Any]":
        search_filter = {id_key: updated_document[id_key]}
        updated_document.update(self._update_time_partial)
        updated = self._update(search_filter=search_filter, update={"$set": updated_document}, upsert=False)
        if updated.modified_count == 0:
            self.insert(document=updated_document)
        return self.find_by_id(search_filter[id_key], id_key=id_key)  # type: ignore[return-value]

    def remove_from_list(self, search_filter: "Dict[str, Any]", *, remove_query: "Dict[str, Any]") -> "UpdateResult":
        return self._update(
            search_filter=search_filter,
            update={"$pull": remove_query, "$set": self._update_time_partial},
            upsert=False,
        )

    def add_to_list(self, search_filter: "Dict[str, Any]", *, add_query: "Dict[str, Any]") -> "UpdateResult":
        return self._update(
            search_filter=search_filter,
            update={"$addToSet": add_query, "$set": self._update_time_partial},
            upsert=False,
        )

    def increment_field(
        self,
        search_filter: "Dict[str, Any]",
        *,
        increment_query: "Dict[str, Any]",
        upsert: bool = False,
    ) -> bool:
        update_result = self._update(
            search_filter=search_filter,
            update={"$inc": increment_query, "$set": self._update_time_partial},
            upsert=upsert,
        )
        return update_result.modified_count != 0

    def aggregate(self, pipeline: "List[Dict[str, Any]]") -> "CommandCursor[Dict[str, Any]]":
        return self.collection.aggregate(pipeline=pipeline)

    def ping(self) -> "Dict[str, Any]":
        return self._mongo_connector.ping()
