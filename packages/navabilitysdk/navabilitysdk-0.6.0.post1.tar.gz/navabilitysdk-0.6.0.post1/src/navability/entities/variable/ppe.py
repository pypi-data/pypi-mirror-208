from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from marshmallow import Schema, fields, post_load

from navability.common.timestamps import TS_FORMAT, TS_FORMAT_NO_TZ

#TODO should we rename to MeanMaxPPE?
@dataclass()
class Ppe:
    id: Optional[UUID]
    solveKey: str
    suggested: List[float]
    max: List[float]
    mean: List[float]
    _type: str
    _version: str
    createdTimestamp: datetime
    lastUpdatedTimestamp: datetime

    def __repr__(self):
        return (
            f"<Ppe(solveKey={self.solveKey},suggested={self.suggested},"
            f"lastUpdatedTimestamp={self.lastUpdatedTimestamp})>"
        )

    def dump(self):
        return Ppe.schema.dump(self)

    def dumps(self):
        return Ppe.schema.dumps(self)

    @staticmethod
    def load(data):
        return PpeSchema().load(data)


class PpeSchema(Schema):
    id = fields.UUID()
    solveKey = fields.Str(required=True)
    suggested = fields.List(fields.Float(), required=True)
    max = fields.List(fields.Float(), required=True)
    mean = fields.List(fields.Float(), required=True)
    _type = fields.Str()
    _version = fields.Str(required=True)
    createdTimestamp = fields.Method(
        "get_timestamp", "set_timestamp", required=True
    )
    lastUpdatedTimestamp = fields.Method(
        "get_timestamp", "set_timestamp", required=True
    )

    class Meta:
        ordered = True

    def get_timestamp(self, obj):
        # Return a robust timestamp
        ts = obj.lastUpdatedTimestamp.isoformat(timespec="milliseconds")
        if not obj.lastUpdatedTimestamp.tzinfo:
            ts += "Z"
        return ts

    def set_timestamp(self, obj):
        # Have to be defensive here because it could be simply serialized
        # or it can be GQL data with formatted
        tsraw = obj if type(obj) == str else obj["formatted"]
        # Defensively append the Z if needed
        try:
            ts = datetime.strptime(tsraw, TS_FORMAT)
        except (ValueError):
            # Fall back with no timezone and assign it.
            # NOTE: This happens with Ppes, we need to update solver Ppes it tz.
            ts = datetime.strptime(tsraw, TS_FORMAT_NO_TZ).replace(tzinfo=timezone.utc)
        return ts

    @post_load
    def marshal(self, data, **kwargs):
        return Ppe(**data)
