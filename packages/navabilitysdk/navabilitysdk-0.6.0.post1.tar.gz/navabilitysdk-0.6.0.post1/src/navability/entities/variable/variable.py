import base64
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from marshmallow import EXCLUDE, Schema, fields, post_load

from navability.common.timestamps import TS_FORMAT
from navability.common.versions import payload_version
from navability.entities.variable.ppe import Ppe, PpeSchema
from navability.entities.blob.blobentry import BlobEntry, BlobEntrySchema
from navability.entities.variable.variablenodedata import (
    VariableNodeData,
    VariableNodeDataSchema,
)


class VariableType(Enum):
    """Variable Type enum, not used in classes until we resolve the
    larger VariableNodeData issues.
    """

    Point2 = "RoME.Point2"
    Pose2 = "RoME.Pose2"
    Pose3 = "RoME.Pose3"
    ContinuousScalar = "IncrementalInference.ContinuousScalar"
    # TBD - https://github.com/JuliaRobotics/Caesar.jl/discussions/810
    Position1 = "IncrementalInference.ContinuousScalar"
    Pose1 = "IncrementalInference.ContinuousScalar"


def _getVariableNodeData(variableType: str, solveKey: str):
    # Not pretty but temporary because I believe we're going to remove
    # VariableNodeData initialization
    if variableType == "RoME.Point2":
        return VariableNodeData(variableType, solveKey, 2)
    if variableType == "RoME.Pose2":
        return VariableNodeData(variableType, solveKey, 3)
    if variableType == "RoME.Pose3":
        return VariableNodeData(variableType, solveKey, 6)
    if variableType == "IncrementalInference.ContinuousScalar":
        return VariableNodeData(variableType, solveKey, 1)
    if variableType == "Position{1}":
        return VariableNodeData(variableType, solveKey, 1)
    raise Exception(f"Variable type '{variableType}' not supported.")


@dataclass()
class VariableSkeleton:
    label: str
    tags: List[str] = field(default_factory=lambda: ["VARIABLE"])
    id: Optional[UUID] = None

    def dump(self):
        return VariableSkeletonSchema().dump(self)

    def dumps(self):
        return VariableSkeletonSchema().dumps(self)

    @staticmethod
    def load(data):
        return VariableSkeletonSchema().load(data)


class VariableSkeletonSchema(Schema):
    id = fields.UUID(required=True)
    label = fields.Str(required=True)
    tags = fields.List(fields.Str(), required=True)

    class Meta:
        ordered = True

    @post_load
    def marshal(self, data, **kwargs):
        return VariableSkeleton(**data)


@dataclass()
class VariableSummary:
    label: str
    variableType: str
    tags: List[str] = field(default_factory=lambda: ["VARIABLE"])
    timestamp: datetime = datetime.utcnow()
    nstime: str = "0"
    # ppes: Dict[str, Ppe] = field(default_factory=lambda: {})
    ppes: List[Ppe] = field(default_factory=lambda: [])
    # blobEntries: Dict[str, BlobEntry] = field(default_factory=lambda: {})
    blobEntries: List[BlobEntry] = field(default_factory=lambda: [])
    _version: str = payload_version
    id: Optional[UUID] = None

    def __repr__(self):
        return (
            f"<VariableSummary(label={self.label},"
            f"variableType={self.variableType},tags={self.tags})>"
        )

    def dump(self):
        return VariableSummarySchema().dump(self)

    def dumps(self):
        return VariableSummarySchema().dumps(self)

    @staticmethod
    def load(data):
        return VariableSummarySchema().load(data)


class VariableSummarySchema(Schema):
    id = fields.UUID()
    label = fields.Str(required=True)
    variableType = fields.Str(required=True)
    tags = fields.List(fields.Str())
    timestamp = fields.Method("get_timestamp", "set_timestamp", required=True)
    nstime = fields.Str(default="0")
    ppes = fields.Nested(PpeSchema, many=True)
    # ppes = fields.Method("get_ppes", "set_ppes")
    blobEntries = fields.Nested(BlobEntrySchema, many=True)
    _version = fields.Str(required=True)

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

    @post_load
    def marshal(self, data, **kwargs):
        return VariableSummary(**data)


@dataclass()
class Variable:
    """A factor graph variable node as well as data carrying object that can serialized and distributed across computing nodes.

    Parameters:
        label: The variable label, such as "x1" or "pose_7"
        variableType: For example "Pose2" or "Pose3"
        tags: A string list of tags for annotating and later searching through nodes, e.g. ["POSE", "VARIABLE", "AUTO"]
        timestamp: When the variable instance occurred.
        nstime: duplicate ns scale time information which does not store full unix time, but rather only the nanosecond portion for higher resolution.
        solvable: indicate whether the variable is ready to be incldued in a solve.
        ppes: Parametric point estimate solutions which summarize the possibly non-Gaussian solution contained in `.solverData`.
        blobEntries: A list of `BlobEntry`s which holds contextual information for (data) `Blob`s stored in a separate `BlobStore`.
        solverData: In depth solver information used for numerical solutions of the factor graph, including non-Gaussian and multiple `solveKeys`.
        metadata: To store opportunistic "small data" that migth be useful to keep.  Use BlobEntries and Blobs as main mechanism for storing heavy lift data.
        _version: Serialization support of Variable objects benefit from knowing the library version used for this object.
        id: Autogenerated uuid4 for use in a distributed system, do not self assign.
    """
    label: str
    variableType: str
    tags: List[str] = field(default_factory=lambda: ["VARIABLE"])
    timestamp: datetime = datetime.utcnow()
    nstime: str = "0"
    solvable: str = 1
    ppes: Dict[str, Ppe] = field(default_factory=lambda: {})
    blobEntries: Dict[str, BlobEntry] = field(default_factory=lambda: {})
    solverData: Dict[str, VariableNodeData] = field(default_factory=lambda: {})
    metadata: dict = field(default_factory=lambda: {})
    _version: str = payload_version
    id: Optional[UUID] = None

    # def __post_init__(self):
    #     pass
    #     if self.solverData == {}:
    #         self.solverData["default"] = _getVariableNodeData(
    #             self.variableType, "default"
    #         )

    def __repr__(self):
        return (
            f"<Variable(label={self.label},variableType={self.variableType},"
            f"tags={self.tags})>"
        )

    def dump(self):
        return VariableSchema().dump(self)

    def dumpPacked(self):
        return PackedVariableSchema().dump(self)

    def dumps(self):
        return VariableSchema().dumps(self)

    def dumpsPacked(self):
        return PackedVariableSchema().dumps(self)

    @staticmethod
    def load(data):
        return VariableSchema().load(data)


class VariableSchema(Schema):
    id = fields.UUID()
    label = fields.Str(required=True)
    variableType = fields.Str(required=True)
    tags = fields.List(fields.Str(), required=True)
    timestamp = fields.Method("get_timestamp", "set_timestamp", required=True)
    nstime = fields.Str(default="0")
    solvable = fields.Int(required=True)
    ppes = fields.Method("get_ppes", "set_ppes")
    blobEntries = fields.Nested(BlobEntrySchema, many=True)
    solverData = fields.Method("get_solverdata", "set_solverdata")
    metadata = fields.Method("get_metadata", "set_metadata")
    _version = fields.Str(required=True)

    class Meta:
        ordered = True
        unknown = EXCLUDE  # Note: This is because of _id, remote and fix later.

    @post_load
    def marshal(self, data, **kwargs):
        return Variable(**data)

    def get_timestamp(self, obj):
        # Return a robust timestamp
        ts = obj.timestamp.isoformat(timespec="milliseconds")
        if not obj.timestamp.tzinfo:
            ts += "Z"
        return ts

    def set_timestamp(self, obj):
        # Have to be defensive here because it could be simply serialized
        # or it can be GQL data with formatted
        tsraw = obj if type(obj) == str else obj["formatted"]
        return datetime.strptime(tsraw, TS_FORMAT)

    def get_solverdata(self, obj):
        return [sd.dump() for sd in obj.solverData.values()]

    def set_solverdata(self, obj):
        return {sd["solveKey"]: VariableNodeData.load(sd) for sd in obj}

    def get_ppes(self, obj):
        return [ppe.dump() for ppe in obj.ppes.values()]

    def set_ppes(self, obj):
        return {ppe["solveKey"]: PpeSchema().load(ppe) for ppe in obj}

    def get_metadata(self, obj):
        return base64.b64encode(json.dumps(obj).encode())

    def set_metadata(self, obj):
        return json.loads(base64.b64decode(obj))


class PackedVariableSchema(Schema):
    """
    A special schema for the addVariable call, which is used to
    form a packed variable struct.
    """

    label = fields.Str(required=True)
    nstime = fields.Str(default="0")
    variableType = fields.Str(required=True)
    ppeDict = fields.Str(attribute="ppes", required=True)
    solverDataDict = fields.Method("get_solver_data_dict", required=True)
    smallData = fields.Str(required=True)
    solvable = fields.Int(required=True)
    tags = fields.List(fields.Str(), required=True)
    timestamp = fields.Method("get_timestamp", required=True)
    _version = fields.Str(required=True)

    class Meta:
        ordered = True

    def get_solver_data_dict(self, obj):
        # TODO: Switch this out to a real embedded object, no need for strings.
        schema = VariableNodeDataSchema()
        vnds = {
            solverKey: schema.dump(vnd) for solverKey, vnd in obj.solverData.items()
        }
        return json.dumps(vnds)

    def get_timestamp(self, obj):
        # Return a robust timestamp
        ts = obj.timestamp.isoformat(timespec="milliseconds")
        if not obj.timestamp.tzinfo:
            ts += "+00"
        return ts
