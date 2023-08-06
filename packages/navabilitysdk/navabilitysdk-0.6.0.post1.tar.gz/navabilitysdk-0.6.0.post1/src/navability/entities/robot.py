from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from marshmallow import Schema, fields, post_load
import base64
import json
import logging

from navability.common.versions import payload_version
from navability.entities.blob.blobentry import BlobEntry, BlobEntrySchema
from navability.entities.session import Session, SessionSchema

logger = logging.getLogger(__name__)

# Define a dataclass for Robot
@dataclass
class Robot:
    id: Optional[UUID]
    label: str
    metadata: dict = field(default_factory=lambda: {})
    blobEntries: List[BlobEntry] = field(default_factory=lambda: [])
    
    _version: str = payload_version
    createdTimestamp: Optional[datetime] = None
    lastUpdatedTimestamp: Optional[datetime] = None

    # Optional
    userLabel: Optional[str] = None
    userId: Optional[UUID] = None
    sessions: Optional[List[Session]] = None


# Define a Marshmallow schema for Robot
class RobotSchema(Schema):
    # Define the required fields and their types
    id = fields.UUID(allow_none=True)
    label = fields.String(required=True)
    _version = fields.String(required=True)
    metadata = fields.Method("get_metadata", "set_metadata")
    blobEntries = fields.Nested(BlobEntrySchema, many=True)
    createdTimestamp = fields.DateTime(allow_none=True)
    lastUpdatedTimestamp = fields.DateTime(allow_none=True)
    
    # Optional
    userLabel = fields.String(allow_none=True)
    userId = fields.UUID(allow_none=True)
    sessions = fields.Nested(SessionSchema, many=True)

    # Define a method to create a Robot object from deserialized data
    @post_load
    def make_robot(self, data, **kwargs):
        return Robot(**data)

    def get_metadata(self, obj):
        return base64.b64encode(json.dumps(obj).encode())

    def set_metadata(self, obj):
        if obj is None or obj.strip() == '':
            logger.warning("Robot metadata is not populated")
            return {}
        return json.loads(base64.b64decode(obj))
