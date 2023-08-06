from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from stringcase import camelcase  # type: ignore[import]


def to_camel(string: str) -> str:
    return camelcase(string)


class Schema(BaseModel):
    """
    A base class for all of Deci's model classes.
    A model stores data in constant fields, and let us manipulate the data in a more readable way.
    """

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        validate_assignment = True
        allow_inf_nan = False

    pass


class DBSchema(Schema):
    update_time: Optional[datetime] = None
    creation_time: Optional[datetime] = None
    id: UUID = Field(default_factory=uuid4)
    deleted: bool = False
