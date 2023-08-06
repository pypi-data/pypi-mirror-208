import base64
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from navability.common.versions import payload_version
from typing import List, Optional
from marshmallow import Schema, fields, post_load

from navability.entities.blob.blobentry import BlobEntry, BlobEntrySchema
from navability.entities.map.map import Map, MapSchema
from navability.entities.robot import Robot, RobotSchema

logger = logging.getLogger(__name__)

# Define a dataclass for User
@dataclass
class User:
    id: Optional[UUID]
    label: str
    sub: str
    givenName: str
    familyName: str
    status: str
    permissions: List[str]
    blobEntries: List[BlobEntry] = field(default_factory=lambda: [])
    metadata: dict = field(default_factory=lambda: {})

    _version: str = payload_version
    createdTimestamp: Optional[datetime] = None 
    lastUpdatedTimestamp: Optional[datetime] = None
    lastAuthenticatedTimestamp: Optional[datetime] = None

    # Optional
    robots: Optional[List[Robot]] = None
    maps: Optional[List[Map]] = None


# Define a Marshmallow schema for User
class UserSchema(Schema):
    # Define the required fields and their types
    id = fields.UUID(allow_none=True)
    sub = fields.String(required=True)
    label = fields.String(required=True)
    givenName = fields.String(required=True)
    familyName = fields.String(required=True)
    status = fields.String(required=True)
    _version = fields.String(allow_none=True)
    permissions = fields.List(fields.String(), required=True)
    metadata = fields.Method("get_metadata", "set_metadata")
    blobEntries = fields.Nested(BlobEntrySchema, many=True)
    createdTimestamp = fields.DateTime(allow_none=True)
    lastUpdatedTimestamp = fields.DateTime(allow_none=True)
    lastAuthenticatedTimestamp = fields.DateTime(allow_none=True)

    # Optional
    robots = fields.Nested(RobotSchema, many=True)
    maps = fields.Nested(MapSchema, many=True)

    # Define a method to create a User object from deserialized data
    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)
    
    def get_metadata(self, obj):
        return base64.b64encode(json.dumps(obj).encode())     

    def set_metadata(self, obj):
        if obj is None or obj.strip() == '':
            logger.warning("User metadata is not populated")
            return {}
        return json.loads(base64.b64decode(obj))
