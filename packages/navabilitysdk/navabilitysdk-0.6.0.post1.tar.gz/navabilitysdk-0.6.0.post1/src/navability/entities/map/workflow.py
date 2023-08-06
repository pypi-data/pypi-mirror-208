from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional
from marshmallow import Schema, fields, post_load
from navability.common.versions import payload_version

# Define a dataclass for Workflow
@dataclass
class Workflow:
    id: Optional[UUID]
    label: str
    description: Optional[str]
    status: str
    _type: str
    data: Optional[str]
    result: Optional[str]
    createdTimestamp: Optional[datetime]
    lastUpdatedTimestamp: Optional[datetime]
    _version: str = payload_version

# Define a Marshmallow schema for Workflow
class WorkflowSchema(Schema):
    # Define the required fields and their types
    id = fields.UUID(allow_none=True)
    label = fields.String(required=True)
    description = fields.String(allow_none=True)
    status = fields.String(required=True)
    _type = fields.String(required=True)
    data = fields.String(allow_none=True)
    result = fields.String(allow_none=True)
    createdTimestamp = fields.DateTime(allow_none=True)
    lastUpdatedTimestamp = fields.DateTime(allow_none=True)
    _version = fields.String(allow_none=True)

    # Define a method to create a Workflow object from deserialized data
    @post_load
    def make_workflow(self, data, **kwargs):
        return Workflow(**data)