import uuid
from datetime import datetime

from pydantic import BaseModel


class RelationshipResponse(BaseModel):
    id: uuid.UUID
    column_name: str
    table_names: list[str]
    file_ids: list[str]
    detected_at: datetime

    model_config = {"from_attributes": True}


class RelationshipListResponse(BaseModel):
    relationships: list[RelationshipResponse]
