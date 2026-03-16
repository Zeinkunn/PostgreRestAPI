from pydantic import BaseModel, Field, conlist, ConfigDict
from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID

class AgentMemoryCreate(BaseModel):
    persona_id: str
    content: str
    embedding: conlist(float, min_length=768, max_length=768)

class AgentMemoryResponse(BaseModel):
    id: UUID
    persona_id: str
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AgentMemorySearch(BaseModel):
    query_embedding: conlist(float, min_length=768, max_length=768)
    persona_id: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=100)

class AgentMemorySearchResponse(AgentMemoryResponse):
    distance: float

class GeneralDataCreate(BaseModel):
    title: str
    description: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

class GeneralDataUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

class GeneralDataResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
