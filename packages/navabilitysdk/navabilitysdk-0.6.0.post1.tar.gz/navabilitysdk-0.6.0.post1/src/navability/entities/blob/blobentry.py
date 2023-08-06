import base64
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from typing import Dict, List, Optional

from marshmallow import EXCLUDE, Schema, fields, post_load

from navability.common.timestamps import TS_FORMAT
from navability.common.versions import payload_version


@dataclass()
class BlobEntry:
    """ A `BlobEntry` is a small about of structured data that holds reference information to find an actual blob. Many `BlobEntry`s 
    can exist on different graph nodes spanning Robots, and Sessions which can all reference the same `Blob`.  A `BlobEntry` 
    is also a equivalent to a bridging entry between local `.originId` and a remotely assigned `.blobIds`.

    All `.blobId`s are unique across the entire distributed system and are immutable.  The `.originId` should be 
    globally unique except for stochastic `uuid4` collisions that cannot be checked from a main reference owing to practical limitations such as network connectivity.

    Args:
        id: Remotely assigned and globally unique identifier for the `BlobEntry` itself (not the `.blobId`).
        label: Human friendly label of the `Blob` and also used as unique identifier per node on which a `BlobEntry` is added.  E.g. do "LEFTCAM_1", "LEFTCAM_2", ... of you need to repeat a label on the same variable.
        blobId: Machine friendly and globally unique identifier of the 'Blob', usually assigned from a common point in the system.  This can be used to guarantee unique retrieval of the large data blob.
        originId: Machine friendly and locally assigned identifier of the 'Blob'.  `.originId`s are mandatory upon first creation at the origin regardless of network access.  Separate from `.blobId` since some architectures do not allow edge processes to assign a uuid to data store elements.
        timestamp: When the Blob itself was first created.
        description: Additional information that can help a different user of the Blob. 
        blobstore: A hint about where the `Blob` itself might be stored.  Remember that a Blob may be duplicated over multiple blobstores.
        hash: A hash value to ensure data consistency which must correspond to the stored hash upon retrieval.  [Legacy: some usage functions allow the check to be skipped if needed.]
        mimeType: MIME description describing the format of binary data in the `Blob`, e.g. 'image/png' or 'application/json; _type=CameraModel'.
        origin: Context from which a BlobEntry=>Blob was first created. E.g. user|robot|session|varlabel.
        metadata: Additional storage for functional metadata used in some scenarios, e.g. to support advanced features such as `parsejson(base64decode(entry.metadata))['time_sync']`.
        createdTimestamp: When the BlobEntry was created.
        lastUpdatedTimestamp: Use carefully, but necessary to support advanced usage such as time synchronization over Blob data.
        _type: Self type declaration for when duck-typing happens.
        _version: Type version of this BlobEntry.
    """
    id: Optional[UUID]
    label: str
    blobId: Optional[UUID]
    originId: UUID
    timestamp: datetime
    description: str
    blobstore: str
    hash: str = ''
    mimeType: str = 'application/octet-stream'
    origin: str = ''
    metadata: dict = field(default_factory=lambda: {})
    
    createdTimestamp: Optional[datetime] = None
    lastUpdatedTimestamp: Optional[datetime] = None
    
    _type: str = "BlobEntry"
    _version: str = payload_version
    # createdTimestamp: datetime # = datetime.utcnow()
    # updatedTimestamp: datetime
    # size: int

    # Optional
    userLabel: Optional[str] = None
    robotLabel: Optional[str] = None
    sessionLabel: Optional[str] = None
    variableLabel: Optional[str] = None
    factorLabel: Optional[str] = None

    def __repr__(self):
        return (
            f"<BlobEntry(label={self.label},"
            f"label={self.label},id={self.id})>"
        )

    def dump(self):
        return BlobEntrySchema().dump(self)

    def dumps(self):
        return BlobEntrySchema().dumps(self)

    @staticmethod
    def load(data):
        return BlobEntrySchema().load(data)


# Legacy BlobEntry_ contract
class BlobEntrySchema(Schema):
    id = fields.UUID()
    label = fields.Str(required=True)
    blobId = fields.UUID()
    originId = fields.UUID()
    timestamp = fields.Method("get_timestamp", "set_timestamp", required=True)
    description = fields.Str(required=True)
    blobstore: str = fields.Str(required=True)
    hash = fields.Str(required=False)
    mimeType = fields.Str(required=False)
    origin = fields.Str(required=False)
    metadata = fields.Method("get_metadata", "set_metadata")
    
    createdTimestamp: datetime = fields.Method("get_timestamp", "set_timestamp", required=False)
    updatedTimestamp: datetime = fields.Method("get_timestamp", "set_timestamp", required=False)
    _type = fields.Str()
    _version = fields.Str(required=True)

    # size: int  = fields.Integer(required=True)
    class Meta:
        ordered = True

    def get_timestamp(self, obj):
        # Return a robust timestamp
        ts = obj.timestamp.isoformat(timespec="milliseconds")
        if not obj.timestamp.tzinfo:
            ts += "+00"
        return ts

    def set_timestamp(self, obj):
        tsraw = obj if type(obj) == str else obj["formatted"]
        return datetime.strptime(tsraw, TS_FORMAT)

    def get_metadata(self, obj):
        return base64.b64encode(json.dumps(obj).encode())

    def set_metadata(self, obj):
        if obj == '':
            return {}
        else:
            return json.loads(base64.b64decode(obj))

    @post_load
    def marshal(self, data, **kwargs):
        return BlobEntry(**data)