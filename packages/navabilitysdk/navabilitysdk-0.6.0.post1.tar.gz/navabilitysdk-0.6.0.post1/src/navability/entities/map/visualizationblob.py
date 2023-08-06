from dataclasses import dataclass
from uuid import UUID
from marshmallow import Schema, fields, post_load

# Define a dataclass for VisualizationBlob
@dataclass
class VisualizationBlob:
    hierarchyId: UUID
    octreeId: UUID
    metadataId: UUID

# Define a Marshmallow schema for VisualizationBlob
class VisualizationBlobSchema(Schema):
    # Define the required fields and their types
    hierarchyId = fields.UUID(required=True)
    octreeId = fields.UUID(required=True)
    metadataId = fields.UUID(required=True)

    # Define a method to create a VisualizationBlob object from deserialized data
    @post_load
    def make_visualization_blob(self, data, **kwargs):
        return VisualizationBlob(**data)