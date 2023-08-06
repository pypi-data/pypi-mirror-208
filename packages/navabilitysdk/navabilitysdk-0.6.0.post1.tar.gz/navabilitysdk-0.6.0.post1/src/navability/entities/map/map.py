from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from marshmallow import Schema, fields, post_load

from navability.entities.session import ( Session, SessionSchema )
from navability.entities.map.workflow import ( Workflow, WorkflowSchema )
from navability.entities.map.annotation import ( Annotation, AnnotationSchema )
from navability.entities.map.affordance import ( Affordance, AffordanceSchema )
from navability.entities.map.visualizationblob import ( VisualizationBlob, VisualizationBlobSchema )

# Define a dataclass for Map
@dataclass
class Map:
    id: Optional[UUID]
    label: str
    description: Optional[str]
    status: str
    data: str
    thumbnailId: Optional[UUID]
    exportedMapId: Optional[UUID]
    annotations: List[Annotation]
    affordances: List[Affordance]
    workflows: List[Workflow]
    sessions: List[Session]
    visualization: Optional[VisualizationBlob]
    createdTimestamp: Optional[datetime]
    lastUpdatedTimestamp: Optional[datetime]

# Define a Marshmallow schema for Map
class MapSchema(Schema):
    # Define the required fields and their types
    id = fields.UUID(allow_none=True)
    label = fields.String(required=True)
    description = fields.String(allow_none=True)
    status = fields.String(required=True)
    data = fields.String(allow_none=True)
    thumbnailId = fields.UUID(allow_none=True)
    exportedMapId = fields.UUID(allow_none=True)
    annotations = fields.Nested(AnnotationSchema, many=True)
    affordances = fields.Nested(AffordanceSchema, many=True)
    workflows = fields.Nested(WorkflowSchema, many=True)
    sessions = fields.Nested(SessionSchema, many=True)
    visualization = fields.Nested(VisualizationBlobSchema, allow_none=True)
    createdTimestamp = fields.DateTime(allow_none=True)
    lastUpdatedTimestamp = fields.DateTime(allow_none=True)

    # Define a method to create a Map object from deserialized data
    @post_load
    def make_map(self, data, **kwargs):
        return Map(**data)