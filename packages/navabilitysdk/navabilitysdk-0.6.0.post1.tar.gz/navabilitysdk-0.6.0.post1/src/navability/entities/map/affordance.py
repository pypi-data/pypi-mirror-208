from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional
from marshmallow import Schema, fields, post_load

# Define a dataclass for Affordance
@dataclass
class Affordance:
    id: Optional[UUID]
    label: str
    position: List[float]
    rotation: List[float]
    scale: List[float]

# Define a Marshmallow schema for Affordance
class AffordanceSchema(Schema):
    # Define the required fields and their types
    id = fields.UUID(allow_none=True)
    label = fields.String(required=True)
    position = fields.List(fields.Float(), required=True)
    rotation = fields.List(fields.Float(), required=True)
    scale = fields.List(fields.Float(), required=True)

    # Define a method to create a Affordance object from deserialized data
    @post_load
    def make_affordance(self, data, **kwargs):
        return Affordance(**data)