from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from marshmallow import Schema, fields, post_load
import base64
import json
import logging

from navability.entities.blob.blobentry import ( BlobEntrySchema, BlobEntry )
from navability.common.versions import payload_version
from navability.entities.factor.factor import Factor, FactorSchema
from navability.entities.variable.variable import Variable, VariableSchema

logger = logging.getLogger(__name__)

# Define a dataclass for Session
@dataclass
class Session:
    id: Optional[UUID]
    label: str
    originLatitude: Optional[str] = None
    originLongitude: Optional[str] = None
    metadata: dict = field(default_factory=lambda: {})
    blobEntries: List[BlobEntry] = field(default_factory=lambda: [])

    _version: str = payload_version
    createdTimestamp: Optional[datetime] = None
    lastUpdatedTimestamp: Optional[datetime] = None

    # Optional
    variables: Optional[List[Variable]] = None
    factors: Optional[List[Factor]] = None
    userLabel: Optional[str] = None
    robotLabel: Optional[str] = None
    robotId: Optional[UUID] = None
    userId: Optional[UUID] = None


# Define a Marshmallow schema for Session
class SessionSchema(Schema):
    # Define the required fields and their types
    id = fields.UUID(allow_none=True)
    label = fields.String(required=True)

    metadata = fields.Method("get_metadata", "set_metadata")
    originLatitude = fields.String(allow_none=True)
    originLongitude = fields.String(allow_none=True)
    createdTimestamp = fields.DateTime(required=True)
    lastUpdatedTimestamp = fields.DateTime(required=True)
    blobEntries = fields.Nested(BlobEntrySchema, many=True)
    _version = fields.String(required=True)

    # Optional
    variables = fields.Nested(VariableSchema, many=True)
    factors = fields.Nested(FactorSchema, many=True)
    userLabel = fields.String(allow_none=True)
    robotLabel = fields.String(allow_none=True)
    robotId = fields.UUID(allow_none=True)
    userId = fields.UUID(allow_none=True)

    # Define a method to create a Session object from deserialized data
    @post_load
    def make_session(self, data, **kwargs):
        return Session(**data)
    
    def get_metadata(self, obj):
        return base64.b64encode(json.dumps(obj).encode())

    def set_metadata(self, obj):
        if obj is None or obj.strip() == '':
            logger.warning("Session metadata is not populated")
            return {}
        return json.loads(base64.b64decode(obj))
