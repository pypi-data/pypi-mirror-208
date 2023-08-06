from typing import TYPE_CHECKING, Generic, TypeVar

from deci_common.abstractions.abstract_logger import ILogger
from deci_common.abstractions.base_model import DBSchema

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Type
    from uuid import UUID

    from deci_common.data_interfaces.mongo_db_interface import MongoDBInterface

T = TypeVar("T", bound=DBSchema)


class DBInterface(Generic[T], ILogger):
    def __init__(self, element_type: "Type[T]", mongo_db_interface: "MongoDBInterface"):
        super().__init__()
        self._element_type = element_type
        self._mongo_db_interface = mongo_db_interface

    def insert(self, element: "T") -> "T":
        """
        Insert an element to the DB and return it
        @param element: The element to insert
        @return: T
        """
        self._mongo_db_interface.insert(element.dict())
        return element

    def find(self, search_filter: "Dict[str, Any]" = {}) -> "List[T]":
        """
        Find all elements from DB with a specified search filter
        @param search_filter: Filter for the search
        @return: List[T]
        """
        elements = self._mongo_db_interface.find(search_filter=search_filter)

        return [self._element_type(**element) for element in elements]

    def find_one(self, search_filter: "Dict[str, Any]" = {}) -> "Optional[T]":
        """
        Find one element from DB with a specified search filter
        @param search_filter: Filter for the search
        @return: Optional[T]
        """
        element = self._mongo_db_interface.find_one(search_filter=search_filter)
        if element is None:
            return None

        return self._element_type(**element)

    def update(self, element: "T") -> "T":
        """
        Updates an element in the DB using its id
        @param element: The element to update to (id is used to find the element to update)
        @return: T
        """
        self._mongo_db_interface.update(search_filter={"id": element.id}, updated_document=element.dict())
        return element

    def update_many(self, updated_document: "Dict[str, Any]", search_filter: "Dict[str, Any]" = {}) -> "List[T]":
        """
        Updates multiple elements in the DB using the specified search filter
        :param updated_document: the new values to set for the documents
        :param search_filter: documents to update values for
        :return: List[T]
        """
        self._mongo_db_interface.update(search_filter=search_filter, updated_document=updated_document)
        return self.find(search_filter=search_filter)

    def delete_many(self, search_filter: "Dict[str, Any]", force: bool = False) -> int:
        """
        Deletes elements from the DB
        @param search_filter: The search filter of the elements to delete
        @param force: if True, permanently delete the elements from the DB, otherwise - just mark them as deleted
        @return: Number of records that were deleted
        """
        if force:
            delete_result = self._mongo_db_interface.delete(search_filter=search_filter)
            return delete_result.deleted_count
        update_result = self._mongo_db_interface.update(search_filter=search_filter, updated_document={"deleted": True})
        return update_result.modified_count

    def delete(self, _id: "UUID", force: bool = False) -> bool:
        """
        Deletes an element from the DB
        @param _id: The ID of the element to delete
        @param force: if True, permanently delete the element from the DB, otherwise - just mark it as deleted
        @return: True on success, False otherwise
        """
        search_filter = {"id": _id}
        return self.delete_many(search_filter, force) == 1

    def increment_fields(self, *, search_filter: "Dict[str, Any]", fields: "Dict[str, int]") -> bool:
        return self._mongo_db_interface.increment_field(search_filter=search_filter, increment_query=fields)
